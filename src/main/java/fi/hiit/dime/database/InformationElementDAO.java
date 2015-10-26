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
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Repository
public class InformationElementDAO {
    private static final Logger LOG = LoggerFactory.getLogger(InformationElementDAO.class);

    @Autowired
    private InfoElemRepository repo;
    private static Set<InformationElement> notIndexed =	new HashSet<InformationElement>();

    public void save(InformationElement obj) {
	obj.autoFill();
	notIndexed.add(obj);
	repo.save(obj);
    }

    public boolean hasUnIndexed() {
	return !notIndexed.isEmpty();
    }

    public Set<InformationElement> getNotIndexed() {
	return notIndexed;
    }

    public void setIndexed(InformationElement elem) {
	elem.isIndexed = true;
	notIndexed.remove(elem);
    }

     public InformationElement expandStub(InformationElement e) {
	if (!e.isStub())
	    return e;

	if (e.getId() != null)
	    return findById(e.getId());

	if (e.appId != null)
	    return repo.findOneByAppId(e.appId);

	return e;
    }

    /**
       Find a single InformationElement by its unique id.

       @param id Unique id of InformationElement object.
       @return The InformationElement object found.
    */
    public InformationElement findById(Long id) {
	return repo.findOne(id);
    }

    /**
       Filtered search for a given user's objects.

       @param userId User id
       @param filterParams Filtering parameters
       @return List of matching information elements
    */
    public List<InformationElement> find(Long userId,
					 Map<String, String> filterParams) 
    {
	return repo.find(User.makeUser(userId), filterParams);
    }

    /**
       Returns number of InformationElement objects which haven't been
       indexed yet.
       
       @return Number of not indexed objects
    */
    public long countNotIndexed() {
	return repo.countByIsIndexed(false);
    }

    /**
       Returns number of InformationElement objects which haven't been
       indexed yet.
       
       @return Number of not indexed objects
    */
    public List<InformationElement> findNotIndexed() {
	return repo.findByIsIndexed(false);
    }

    /**
       Returns all InformationElement objects.
    */
    public Iterable<InformationElement> findAll() {
    	return repo.findAll();
    }

    /**
       Return all InformationElement objects in database.
       
       @param id User id
       @return List of all InformationElement objects for user
    */
    public List<InformationElement> elementsForUser(Long id) {
	return repo.findByUser(User.makeUser(id));
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

