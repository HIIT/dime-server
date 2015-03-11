package fi.hiit.dime.database;

import java.util.List;
import org.springframework.data.mongodb.repository.MongoRepository;

import org.springframework.data.mongodb.core.aggregation.Aggregation;
import org.springframework.data.mongodb.core.aggregation.AggregationResults;
import static org.springframework.data.mongodb.core.aggregation.Aggregation.*;
import org.springframework.data.domain.Sort.Direction;
import org.springframework.beans.factory.annotation.Autowired;

import org.springframework.data.mongodb.core.MongoOperations;

import org.springframework.util.Assert;


import org.springframework.data.mongodb.core.query.Query;


import java.util.List;
import java.util.ArrayList;


import fi.hiit.dime.data.ZgEvent;

interface CustomZgEventRepository {
    List<ZgCount> zgHist(String groupBy, boolean percentage);
}

class ZgEventRepositoryImpl implements CustomZgEventRepository {
    private final MongoOperations operations;

    @Autowired
    public ZgEventRepositoryImpl(MongoOperations operations) {
	Assert.notNull(operations, "MongoOperations must not be null!");
	this.operations = operations;
    }

    public List<ZgCount> zgHist(String groupBy, boolean percentage) {
	// db.zgEvent.aggregate([{ $group: { _id: "$actor", nevents: { $sum: 1 } } }])

	Aggregation agg = newAggregation(group(groupBy).count().as("nevents"),
					 project("nevents").and(groupBy).previousOperation(),
					 sort(Direction.DESC, "nevents"));
	AggregationResults<ZgCount> results = operations.aggregate(agg, "zgEvent", ZgCount.class);
	List<ZgCount> zgCounts = results.getMappedResults();

	if (percentage) {
	    long total = operations.count(new Query(), "zgEvent");
	    for (ZgCount zgc : zgCounts) {
		zgc.percentage = 100.0*zgc.nevents/total;
	    }
	}
	return zgCounts;
    }

}

public interface ZgEventRepository extends MongoRepository<ZgEvent, String>, CustomZgEventRepository {
    public List<ZgEvent> findAllByOrderByTimestampDesc();
}
