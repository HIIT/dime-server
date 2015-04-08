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

// FIXME use mongotemplates instead
// http://docs.spring.io/spring-data/data-mongo/docs/1.7.0.RELEASE/reference/html/#mongo-template

//------------------------------------------------------------------------------

import fi.hiit.dime.data.ZgEvent;
import java.util.ArrayList;
import java.util.List;
import java.util.List;
import org.bson.types.ObjectId;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Sort.Direction;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.data.mongodb.core.aggregation.Aggregation;
import org.springframework.data.mongodb.core.aggregation.AggregationResults;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.util.Assert;
import static org.springframework.data.mongodb.core.aggregation.Aggregation.*;
import static org.springframework.data.mongodb.core.query.Criteria.where;
import static org.springframework.data.mongodb.core.query.Query.query;

//------------------------------------------------------------------------------

interface CustomZgEventRepository {
    List<ZgCount> zgHist(String groupBy, boolean percentage);
    List<ZgEvent> eventsForUser(String id);
}

class ZgEventRepositoryImpl implements CustomZgEventRepository {
    private final MongoOperations operations;

    @Autowired
    public ZgEventRepositoryImpl(MongoOperations operations) {
	Assert.notNull(operations, "MongoOperations must not be null!");
	this.operations = operations;
    }

    @Override
    public List<ZgCount> zgHist(String groupBy, boolean percentage) {
	// db.zgEvent.aggregate([{ $group: { _id: "$actor", nevents: { $sum: 1 } } }])

	Aggregation agg =
	    newAggregation(group(groupBy).count().as("nevents"),
			   project("nevents").and(groupBy).previousOperation(),
			   sort(Direction.DESC, "nevents"));
	AggregationResults<ZgCount> results =
	    operations.aggregate(agg, "zgEvent", ZgCount.class);
	List<ZgCount> zgCounts = results.getMappedResults();

	if (percentage) {
	    long total = operations.count(new Query(), "zgEvent");
	    for (ZgCount zgc : zgCounts) {
		zgc.percentage = 100.0*zgc.nevents/total;
	    }
	}
	return zgCounts;
    }

    @Override
    public List<ZgEvent> eventsForUser(String id) {
	return operations.find(query(where("user._id").is(new ObjectId(id))).
				     with(new Sort(Sort.Direction.DESC,  "timestamp")),
			       ZgEvent.class, "zgEvent");
    }
    
}

public interface ZgEventRepository extends MongoRepository<ZgEvent, String>, CustomZgEventRepository {
    // public List<ZgEvent> findAllByOrderByTimestampDesc();
    public List<ZgEvent> findByIdOrderByTimestampDesc(String id);
}
