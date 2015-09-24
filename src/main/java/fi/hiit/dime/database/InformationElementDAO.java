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

import fi.hiit.dime.data.*;

import com.mongodb.BasicDBList;
import com.mongodb.BasicDBObject;
import com.mongodb.CommandResult;
import com.mongodb.DBObject;
import org.bson.types.ObjectId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort.Direction;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.data.mongodb.core.query.*;
import org.springframework.stereotype.Repository;
import org.springframework.util.Assert;
import static org.springframework.data.mongodb.core.query.Criteria.where;
import static org.springframework.data.mongodb.core.query.Query.query;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

@Repository
public class InformationElementDAO extends BaseDAO<InformationElement> {
    private static final Logger LOG = LoggerFactory.getLogger(InformationElementDAO.class);

    @Override
    public String collectionName() { 
	return "informationElement";
    }

    /**
       Find a single InformationElement by its unique id.

       @param id Unique id of InformationElement object.
       @return The InformationElement object found.
    */
    public InformationElement findById(String id) {
    	return operations.findById(id, InformationElement.class, collectionName());
    }

    /**
       Perform a text search.

       @param query Text query string
       @param limit Limit results list to this many objects
       @param userId Id of user to search from

       @return list of InformationElement objects found in search
    */
    public List<InformationElement> textSearch(String query, int limit, String userId) {
	ensureTextIndex("plainTextContent");

	int[] version = getMongoVersion();

	// Filter out other users
	Criteria filterCriteria = where("user._id").is(new ObjectId(userId));

	// For mongodb versions >= 2.6, we can use the new TextQuery
	// interface
	if (version[0] >= 3 || (version[0] >= 2 && version[1] >= 6)) {
	    Query dbQuery = new TextQuery(query)
		.sortByScore()
		.addCriteria(filterCriteria);
	    
	    if (limit != -1)
		dbQuery = dbQuery.with(new PageRequest(0, limit));

	    return operations.find(dbQuery, InformationElement.class, collectionName());


	} else if (version[0] == 2 && version[1] >= 4) {
	    LOG.warn("Using deprecated mongodb 2.4 interface for text query.");

	   // For version 2.4 we use the raw mongodb command, e.g.
	   // db.zgSubject.runCommand( "text", { search: "SEARCH QUERY" } )
	   // http://docs.mongodb.org/v2.4/reference/command/text/#dbcmd.text

	    DBObject command = new BasicDBObject();
	    command.put("text", collectionName());
	    command.put("search", query);
	    command.put("filter", query(filterCriteria).getQueryObject());
	    // command.put("limit", n);
	    // command.put("project", new BasicDBObject("_id", 1));

	    CommandResult commandResult = operations.executeCommand(command);

	    // Construct List<InformationElements> to return out of the
	    // CommandResult
	    List<InformationElement> results =
		new ArrayList<InformationElement>();

	    BasicDBList resultList = (BasicDBList)commandResult.get("results");
	    if (resultList == null) // return empty list if there are no results
		return results;

	    Iterator<Object> it = resultList.iterator();
	    while (it.hasNext()) {
		BasicDBObject resultContainer = (BasicDBObject)it.next();
		BasicDBObject resultObject = (BasicDBObject)resultContainer.get("obj");
		
		InformationElement sub = operations.getConverter().
		    read(InformationElement.class, resultObject);
		
		results.add(sub);
	    }

	    return results;
	} else {
	    return new ArrayList<InformationElement>();
	}
    }

    public List<InformationElement> find(String userId, Map<String, String> filterParams) {
	ensureIndex("start");

	Criteria search = where("user._id").is(new ObjectId(userId));

	for (Map.Entry<String, String> param : filterParams.entrySet()) {
	    String name = param.getKey();
	    String value = param.getValue();

	    switch (name) {
	    case "tag":
		name = "tags";
		break;
	    case "uri":
	    case "plainTextContent":
	    case "isStoredAs":
	    case "typeStoredAs":
	    case "mimeType":
	    case "title":
	    // case "":
		break;
	    default:
		throw new IllegalArgumentException(name);
	    }
	    search = search.and(name).is(value);
	}

	return operations.find(query(search).
			       with(new Sort(Sort.Direction.DESC, "start")).
			       limit(100),
			       InformationElement.class, collectionName());
    }


    /**
       Return all InformationElement objects in database.
       
       @param id User id
       @return List of all InformationElement objects for user
    */
    public List<InformationElement> elementsForUser(String id) {
	return operations.find(query(where("user._id").is(new ObjectId(id))),
			       InformationElement.class, collectionName());
    }

    /**
       Removes all items for user.

       @param id User id
       @return Number of items removed.
    */
    public int removeForUser(String id) {
	return operations.remove(query(where("user._id").is(new ObjectId(id))),
				 InformationElement.class, collectionName()).getN();
    }
}

