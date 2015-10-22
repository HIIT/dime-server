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
import fi.hiit.dime.authentication.User;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;

@Repository
public class EventDAO {
    private static final Logger LOG = LoggerFactory.getLogger(EventDAO.class);

    @Autowired
    private EventRepository repo;

    public void save(Event obj) {
	obj.autoFill();
	repo.save(obj);
    }

    public Event findById(String id) {
	return repo.findOne(id);
    }

    /**
       Filtered search for a given user's events.

       @param userId User id
       @param filterParams Filtering parameters
       @return List of matching events
    */
    public List<Event> find(String userId, Map<String, String> filterParams) {
	return repo.find(User.makeUser(userId), filterParams);
    }

    public List<Event> eventsForUser(String userId) {
	return repo.findByUserOrderByStartDesc(User.makeUser(userId));
    }

    public long count(String id) {
	return repo.countByUser(User.makeUser(id));
    }

    @Transactional
    public long removeForUser(String id) {
	return repo.deleteByUser(User.makeUser(id));
    }
    
}
