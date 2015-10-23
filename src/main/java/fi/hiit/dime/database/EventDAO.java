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

import fi.hiit.dime.data.Event;

import org.bson.types.ObjectId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Sort.Direction;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.data.mongodb.core.aggregation.Aggregation;
import org.springframework.data.mongodb.core.aggregation.AggregationResults;
import org.springframework.stereotype.Repository;
import org.springframework.util.Assert;
import org.springframework.data.mongodb.core.query.Criteria;
import static org.springframework.data.mongodb.core.aggregation.Aggregation.*;
import static org.springframework.data.mongodb.core.query.Criteria.where;
import static org.springframework.data.mongodb.core.query.Query.query;

import com.mongodb.WriteResult;

import java.util.Date;
import java.util.Enumeration;
import java.util.List;
import java.util.Map;

@Repository
public class EventDAO extends BaseDAO<Event> {
    private static final Logger LOG = 
	LoggerFactory.getLogger(EventDAO.class);

    @Override
    public String collectionName() { 
	return "event";
    }

    @Override
    public void save(Event obj) {
	obj.autoFill();
	super.save(obj);
    }

    public List<EventCount> eventHist(String groupBy, Date fromDate, Date toDate,
				      boolean percentage) {
	/* This should do the same as the following mongodb code:

	db.zgEvent.aggregate([
	    { $match : { 
		timestamp : { 
		    $gte : ISODate("2015-04-22T00:00:00.000Z"), 
		    $lt : ISODate("2015-04-23T00:00:00.000Z") 
		} 
	    } },
	    { $group: { 
		_id: "$actor", 
		nevents: { $sum: 1 } 
	    } }
	])
	*/

	Aggregation agg =
	    newAggregation(match(where("start").gte(fromDate).lt(toDate)),
			   group(groupBy).count().as("nevents"),
			   project("nevents").and(groupBy).previousOperation(),
			   sort(Direction.DESC, "nevents"));
	AggregationResults<EventCount> results =
	    operations.aggregate(agg, collectionName(), EventCount.class);
	List<EventCount> eventCounts = results.getMappedResults();

	if (percentage) {
	    int total = 0;
	    for (EventCount evc : eventCounts) {
		total += evc.nevents;
	    }

	    for (EventCount evc : eventCounts) {
		evc.percentage = 100.0*evc.nevents/total;
	    }
	}
	return eventCounts;
    }

    public Event findById(String id) {
    	return operations.findById(id, Event.class, collectionName());
    }

    public List<Event> find(String userId, Map<String, String> filterParams) {
	ensureIndex("start");

	Criteria search = where("user._id").is(new ObjectId(userId));

	for (Map.Entry<String, String> param : filterParams.entrySet()) {
	    String name = param.getKey();
	    String value = param.getValue();

	    switch (name) {
	    case "tag":
		name = "tags";
		break;
	    case "actor":
	    case "origin":
	    case "type":
	    // case "start":
	    // case "end":
	    // case "duration":
	    case "query":
	    // case "":
		break;
	    default:
		throw new IllegalArgumentException(name);
	    }
	    search = search.and(name).is(value);
	}

	return operations.find(query(search).
			       with(new Sort(Sort.Direction.DESC, "start")),
			       Event.class, collectionName());
    }

    public List<Event> eventsForUser(String userId) {
	ensureIndex("start");

	return operations.find(query(where("user._id").is(new ObjectId(userId))).
			       with(new Sort(Sort.Direction.DESC, "start")).
			       limit(100),
			       Event.class, collectionName());
    }

    public long count(String id) {
	return operations.count(query(where("user._id").is(new ObjectId(id))),
				Event.class, collectionName());
    }

    public int removeForUser(String id) {
	return operations.remove(query(where("user._id").is(new ObjectId(id))),
				 Event.class, collectionName()).getN();
    }
    
}
