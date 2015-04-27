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

import com.mongodb.BasicDBList;
import com.mongodb.BasicDBObject;
import com.mongodb.CommandResult;
import com.mongodb.DBObject;
import fi.hiit.dime.data.ZgSubject;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import org.bson.types.ObjectId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.mongodb.core.query.TextCriteria;
import org.springframework.data.mongodb.core.query.TextQuery;
import org.springframework.stereotype.Repository;
import org.springframework.util.Assert;
import static org.springframework.data.mongodb.core.query.Criteria.where;
import static org.springframework.data.mongodb.core.query.Query.query;

//------------------------------------------------------------------------------

@Repository
public class ZgSubjectDAO extends BaseDAO<ZgSubject> {
    private static final Logger LOG = LoggerFactory.getLogger(ZgSubjectDAO.class);

    @Override
    public String collectionName() { 
	return "zgSubject";
    }

    //--------------------------------------------------------------------------

    public ZgSubject findById(String id) {
    	return operations.findById(id, ZgSubject.class, collectionName());
    }

    //--------------------------------------------------------------------------

    public List<ZgSubject> textSearch(String query, String userId) {
	int[] version = getMongoVersion();

	// Filter out other users
	Criteria filterCriteria = where("user._id").is(new ObjectId(userId));

	// For mongodb versions >= 2.6, we can use the new TextQuery
	// interface
	if (version[0] >= 3 || (version[0] >= 2 && version[1] >= 6)) {
	    System.out.println("Using new text query");
	    Query dbQuery = TextQuery.queryText(new TextCriteria().matchingPhrase(query)).sortByScore().addCriteria(filterCriteria); 
	    return operations.find(dbQuery, ZgSubject.class);
	} else if (version[0] == 2 && version[1] >= 4) {
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

	    // Construct List<ZgSubjects> to return out of the
	    // CommandResult
	    List<ZgSubject> results = new ArrayList<ZgSubject>();

	    BasicDBList resultList = (BasicDBList)commandResult.get("results");
	    if (resultList == null) // return empty list if there are no results
		return results;

	    Iterator<Object> it = resultList.iterator();
	    while (it.hasNext()) {
		BasicDBObject resultContainer = (BasicDBObject)it.next();
		BasicDBObject resultObject = (BasicDBObject)resultContainer.get("obj");
		
		ZgSubject sub = operations.getConverter().read(ZgSubject.class, resultObject);
		
		results.add(sub);
	    }

	    return results;
	} else {
	    return new ArrayList<ZgSubject>();
	}
    }
}

