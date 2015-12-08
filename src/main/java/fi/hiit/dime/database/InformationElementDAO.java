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

import fi.hiit.dime.data.InformationElement;
import fi.hiit.dime.authentication.User;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.Date;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

@Service
public class InformationElementDAO extends BaseDAO<InformationElement> {
    private static final Logger LOG = LoggerFactory.getLogger(InformationElementDAO.class);

    @Autowired
    private InfoElemRepository repo;

    @Transactional
    public void save(InformationElement obj) {
	if (obj.timeCreated == null)
	    obj.timeCreated = new Date();
	obj.timeModified = new Date();

	notIndexed.add(obj);
	repo.save(obj);
    }

    @Transactional
    public InformationElement replace(InformationElement oldObj, 
				      InformationElement newObj) {
	newObj.timeModified = new Date();
	return repo.replace(oldObj, newObj);
    }

    /**
       Find a single InformationElement by its unique id.

       @param id Unique id of InformationElement object.
       @return The InformationElement object found.
    */
    @Transactional(readOnly = true)
    public InformationElement findById(Long id) {
	return repo.findOne(id);
    }

    /**
       Find a single InformationElement by its unique id, and user.

       @param id Unique id of InformationElement object.
       @param user User
       @return The InformationElement object found.
    */
    @Transactional(readOnly = true)
    public InformationElement findById(Long id, User user) {
	return repo.findOneByIdAndUser(id, user);
    }

    /**
       Find a single InformationElement by its appId.

       @param appId Appliction id
       @param user User
       @return The InformationElement object found.
    */
    @Transactional(readOnly = true)
    public InformationElement findByAppId(String appId, User user) {
	return repo.findOneByAppIdAndUser(appId, user);
    }

    /**
       Filtered search for a given user's objects.

       @param userId User id
       @param filterParams Filtering parameters
       @return List of matching information elements
    */
    @Transactional(readOnly = true)
    public List<InformationElement> find(Long userId,
					 Map<String, String> filterParams) 
    {
	return repo.find(User.makeUser(userId), filterParams);
    }

    /**
       Returns all InformationElement objects.
    */
    @Transactional(readOnly = true)
    public Iterable<InformationElement> findAll() {
    	return repo.findAll();
    }

    /**
       Return all InformationElement objects in database.
       
       @param id User id
       @return List of all InformationElement objects for user
    */
    @Transactional(readOnly = true)
    public List<InformationElement> elementsForUser(Long id, int limit) {
	return repo.findByUserOrderByTimeModifiedDesc(User.makeUser(id),
					       new PageRequest(0, limit));
    }

    @Transactional(readOnly = true)
    public long count(Long id) {
	return repo.countByUser(User.makeUser(id));
    }

    /**
       Removes all items for user.

       @param id User id
       @return Number of items removed.
    */
    @Transactional
    public long removeForUser(Long id) {
 	return repo.deleteByUser(User.makeUser(id));
    }
}

