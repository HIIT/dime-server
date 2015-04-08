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

import fi.hiit.dime.data.ZgSubject;
import java.util.ArrayList;
import java.util.List;
import java.util.Iterator;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.mongodb.core.query.TextCriteria;
import org.springframework.data.mongodb.core.query.TextQuery;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.util.Assert;
import com.mongodb.CommandResult;
import com.mongodb.DBObject;
import com.mongodb.BasicDBObject;
import com.mongodb.BasicDBList;

//------------------------------------------------------------------------------

interface CustomZgSubjectRepository {
    List<ZgSubject> textSearch(String query);
}

//------------------------------------------------------------------------------

class ZgSubjectRepositoryImpl implements CustomZgSubjectRepository {
    private final MongoOperations operations;

    @Autowired
    public ZgSubjectRepositoryImpl(MongoOperations operations) {
	Assert.notNull(operations, "MongoOperations must not be null!");
	this.operations = operations;
    }

    @Override
    public List<ZgSubject> textSearch(String query) {
	/* NOTE: this should work with mongodb 2.6, but does not work
	   with 2.4.9 at least */

	// Query dbQuery = TextQuery.queryText(new
	// TextCriteria().matchingPhrase(query)).sortByScore(); Query
	// dbQuery = new TextQuery(query); return
	// operations.find(dbQuery, ZgSubject.class);

	DBObject command = new BasicDBObject();
	command.put("text", "zgSubject");
	command.put("search", query);
        // command.put("filter", Query.query(filterCriteria).getQueryObject());
        // command.put("limit", countAll());
        // command.put("project", new BasicDBObject("_id", 1));

	CommandResult commandResult = operations.executeCommand(command);

	List<ZgSubject> results = new ArrayList<ZgSubject>();

        BasicDBList resultList = (BasicDBList)commandResult.get("results");
        if (resultList == null)
	    return results;

        Iterator<Object> it = resultList.iterator();
        while (it.hasNext()) {
            BasicDBObject resultContainer = (BasicDBObject)it.next();
            BasicDBObject resultObject = (BasicDBObject)resultContainer.get("obj");

	    ZgSubject sub = operations.getConverter().read(ZgSubject.class, resultObject);

	    results.add(sub);
        }

	return results;
    }
}

//------------------------------------------------------------------------------

public interface ZgSubjectRepository extends MongoRepository<ZgSubject, String>, CustomZgSubjectRepository {
}
