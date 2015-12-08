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
import fi.hiit.dime.data.InformationElement;
import fi.hiit.dime.data.ResourcedEvent;
import fi.hiit.dime.authentication.User;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.List;
import java.util.Map;

@Service
public class EventDAO extends BaseDAO<Event> {
    private static final Logger LOG = LoggerFactory.getLogger(EventDAO.class);

    @Autowired
    private EventRepository repo;

    @Transactional
    public void save(Event obj) {
	if (obj.timeCreated == null)
	    obj.timeCreated = new Date();
	obj.timeModified = new Date();

	notIndexed.add(obj);
	repo.save(obj);
    }

    @Transactional
    public Event replace(Event oldObj, Event newObj) {
	newObj.timeModified = new Date();
	return repo.replace(oldObj, newObj);
    }

    @Transactional(readOnly = true)
    public Event findById(Long id) {
	return repo.findOne(id);
    }

    @Transactional(readOnly = true)
    public Event findById(Long id, User user) {
	return repo.findOneByIdAndUser(id, user);
    }

    @Transactional(readOnly = true)
    public Event findByAppId(String appId, User user) {
	return repo.findOneByAppIdAndUser(appId, user);
    }

    @Transactional(readOnly = true)
    public Iterable<Event> findAll() {
    	return repo.findAll();
    }

    @Transactional(readOnly = true)
    public List<ResourcedEvent> findByElement(InformationElement elem, User user) {
	return repo.findByTargettedResourceAndUser(elem, user);
    }

    /**
       Filtered search for a given user's events.

       @param userId User id
       @param filterParams Filtering parameters
       @return List of matching events
    */
    @Transactional(readOnly = true)
    public List<Event> find(Long userId, Map<String, String> filterParams) {
	return repo.find(User.makeUser(userId), filterParams);
    }

    @Transactional(readOnly = true)
    public List<Event> eventsForUser(Long userId, int limit) {
	return repo.findByUserOrderByStartDesc(User.makeUser(userId),
					       new PageRequest(0, limit));
    }

    @Transactional(readOnly = true)
    public long count(Long id) {
	return repo.countByUser(User.makeUser(id));
    }

    @Transactional
    public long removeForUser(Long id) {
	return repo.deleteByUser(User.makeUser(id));
    }

    @Transactional(readOnly = true)
    public List<Event> eventsSince(Long userId, Date since) {
	return repo.findByUserAndStartIsAfterOrderByStartDesc(User.makeUser(userId), since);
    }
    
}
