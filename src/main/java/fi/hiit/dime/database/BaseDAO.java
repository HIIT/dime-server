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

import fi.hiit.dime.AppConfig;

import com.mongodb.BasicDBList;
import com.mongodb.BasicDBObject;
import com.mongodb.CommandResult;
import com.mongodb.DBCollection;
import com.mongodb.Mongo;
import com.mongodb.WriteResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoOperations;
import static org.springframework.data.mongodb.core.query.Criteria.where;
import static org.springframework.data.mongodb.core.query.Query.query;
import static org.springframework.data.mongodb.core.query.Update.update;

import java.util.Iterator;

abstract class BaseDAO<T extends Object> {
    private static final Logger LOG = LoggerFactory.getLogger(BaseDAO.class);

    @Autowired
    protected MongoOperations operations;

    @Autowired
    protected Mongo mongo;

    private static int[] version = null;

    public <T> T findById(String id, Class<T> entityClass) {
    	return operations.findById(id, entityClass, collectionName());
    }

    public void save(T obj) {
	operations.save(obj, collectionName());
    }

    abstract public String collectionName();

    public DBCollection getCollection() {
	return operations.getCollection(collectionName());
    }

    public void ensureIndex(String fieldName, Object value) {
	getCollection().createIndex(new BasicDBObject(fieldName, value));
    }

    public void ensureIndex(String fieldName) {
	getCollection().createIndex(new BasicDBObject(fieldName, 1));
    }

    public void ensureTextIndex(String fieldName) {
	getCollection().createIndex(new BasicDBObject(fieldName, "text"));
    }

    /**
       Helper method to find missing fields and set them to a default
       value. Useful when the object definition has been modified and
       old objects need to be updated.

       @param fieldName Name of field to check for
       @param value Default value for setting the field
    */
    protected int fixMissingField(String fieldName, Object value) {
	WriteResult res =
	    operations.updateMulti(query(where(fieldName).exists(false)),
				   update(fieldName, value),
				   collectionName());
	return res.getN();
    }

    /**
     * Get mongodb server version as an array of ints, e.g. {2, 4, 9}
     * for version 2.4.9.
     * @return MongoDB version 
     */
    public int[] getMongoVersion() {
	if (version == null) {
	    CommandResult result = mongo.getDB(AppConfig.DB_NAME).command("buildinfo");

	    BasicDBList resultList = (BasicDBList)result.get("versionArray");
	    if (resultList == null) 
		return null;

	    version = new int[resultList.size()];
	    for (int i=0; i<resultList.size(); i++) 
		version[i] = (Integer)resultList.get(i);
	}
	return version;
    }

}
