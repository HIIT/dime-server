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

import org.springframework.data.domain.Pageable;
import org.springframework.data.repository.CrudRepository;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.persistence.TypedQuery;

interface EventRepositoryCustom {
    public List<Event> find(User user, Map<String, String> filterParams);
    public Event replace(Event oldEvent, Event newEvent);
}

class EventRepositoryImpl extends BaseRepository implements EventRepositoryCustom {

    public List<Event> find(User user, Map<String, String> filterParams) {
	// We build the SQL query into q
	StringBuilder q = new StringBuilder("select e from Event e");

	// To keep track if we are at the first search parameter
	boolean first = true;

	// Map for storing named parameters for the query we are
	// constructing
	Map<String, String> namedParams = new HashMap<String, String>();

	// Loop over user's parameters, and transform to SQL statments
	// and fill in namedParams
	for (Map.Entry<String, String> param : filterParams.entrySet()) {
    	    String name = param.getKey();
    	    String value = param.getValue();

    	    switch (name) {
    	    // case "tag":
    	    // 	name = "tags";
    	    // 	break;
    	    case "actor":
    	    case "origin":
    	    case "type":
    	    // case "start":
    	    // case "end":
    	    // case "duration":
    	    case "query":
    	    // case "":
    		break;
    	    default:
    		throw new IllegalArgumentException(name);
    	    }

	    if (first) {
		q.append(" where");
		first = false;
	    } else {
		q.append(" and");
	    }
	    
	    q.append(String.format(" %s=:%s", name, name));
	    namedParams.put(name, value);
    	}

	return makeQuery(q.toString(), namedParams, Event.class).getResultList();
    }

    public Event replace(Event oldEvent, Event newEvent) {
	newEvent.copyIdFrom(oldEvent);
	return entityManager.merge(newEvent);
    }
}

public interface EventRepository extends CrudRepository<Event, Long>,
					 EventRepositoryCustom {
    Event findOne(Long id);

    Event findOneByIdAndUser(Long id, User user);

    Event findOneByAppIdAndUser(String appId, User user);

    List<Event> findByUserOrderByStartDesc(User user, Pageable pageable);

    Long countByUser(User user);

    Long deleteByUser(User user);
}

