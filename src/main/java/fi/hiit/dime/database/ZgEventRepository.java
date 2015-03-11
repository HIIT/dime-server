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

import java.util.List;
import java.util.ArrayList;


import fi.hiit.dime.data.ZgEvent;

interface CustomZgEventRepository {
    List<ZgCount> zgHist();
}

class ZgEventRepositoryImpl implements CustomZgEventRepository {
    private final MongoOperations operations;

    @Autowired
    public ZgEventRepositoryImpl(MongoOperations operations) {
	Assert.notNull(operations, "MongoOperations must not be null!");
	this.operations = operations;
    }

    public List<ZgCount> zgHist() {
	// db.zgEvent.aggregate([{ $group: { _id: "$actor", nevents: { $sum: 1 } } }])

	Aggregation agg = newAggregation(group("actor").count().as("nevents"),
					 project("nevents").and("actor").previousOperation(),
					 sort(Direction.DESC, "nevents"));
	AggregationResults<ZgCount> results = operations.aggregate(agg, "zgEvent", ZgCount.class);
	List<ZgCount> zgCounts = results.getMappedResults();
	return zgCounts;
    }

}

public interface ZgEventRepository extends MongoRepository<ZgEvent, String>, CustomZgEventRepository {
    public List<ZgEvent> findAllByOrderByTimestampDesc();
}
