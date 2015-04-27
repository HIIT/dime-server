/*
  Copyright (c) 2015 University of Helsinki

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation files
  (the "Software"), to deal in the Software without restriction,
  including without limitation the rights to use, copy, modify, merge,
  publish, distribute, sublicense, and/or sell copies of the Software,
  and to permit persons to whom the Software is furnished to do so,
  subject to the following conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
*/

package fi.hiit.dime.database;

//------------------------------------------------------------------------------

import fi.hiit.dime.data.ZgEvent;
import java.util.Date;
import java.util.List;
import org.bson.types.ObjectId;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Sort.Direction;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.data.mongodb.core.aggregation.Aggregation;
import org.springframework.data.mongodb.core.aggregation.AggregationResults;
// import org.springframework.data.mongodb.core.query.Query;
import org.springframework.util.Assert;
import static org.springframework.data.mongodb.core.aggregation.Aggregation.*;
import static org.springframework.data.mongodb.core.query.Criteria.where;
import static org.springframework.data.mongodb.core.query.Query.query;
import org.springframework.stereotype.Repository;

//------------------------------------------------------------------------------

@Repository
public class ZgEventDAO extends BaseDAO<ZgEvent> {

    @Override
    public String collectionName() { 
	return "zgEvent";
    }

    //--------------------------------------------------------------------------

    public List<ZgCount> zgHist(String groupBy, Date fromDate, Date toDate,
				boolean percentage) {
	// db.zgEvent.aggregate([
	//     { $match : { 
	// 	timestamp : { 
	// 	    $gte : ISODate("2015-04-22T00:00:00.000Z"), 
	// 	    $lt : ISODate("2015-04-23T00:00:00.000Z") 
	// 	} 
	//     } },
	//     { $group: { 
	// 	_id: "$actor", 
	// 	nevents: { $sum: 1 } 
	//     } }
	// ])

	// System.out.println("ZGHIST: " + fromDate + " " + toDate);

	Aggregation agg =
	    newAggregation(match(where("timestamp").gte(fromDate).lt(toDate)),
			   group(groupBy).count().as("nevents"),
			   project("nevents").and(groupBy).previousOperation(),
			   sort(Direction.DESC, "nevents"));
	AggregationResults<ZgCount> results =
	    operations.aggregate(agg, collectionName(), ZgCount.class);
	List<ZgCount> zgCounts = results.getMappedResults();

	if (percentage) {
	    int total = 0;
	    for (ZgCount zgc : zgCounts) {
		total += zgc.nevents;
	    }

	    for (ZgCount zgc : zgCounts) {
		zgc.percentage = 100.0*zgc.nevents/total;
	    }
	}
	return zgCounts;
    }

    //--------------------------------------------------------------------------

    public List<ZgEvent> eventsForUser(String id) {
	return operations.find(query(where("user._id").is(new ObjectId(id))).
				     with(new Sort(Sort.Direction.DESC,  "timestamp")),
			       ZgEvent.class, collectionName());
    }
    
}
