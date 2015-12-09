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

import org.springframework.data.domain.Pageable;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.ArrayList;
import java.util.Date;
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
	StringBuilder q = new StringBuilder("select e from Event e where user.id=:userId");

	// Map for storing named parameters for the query we are
	// constructing
	Map<String, String> namedParams = new HashMap<String, String>();

	// Loop over user's parameters, and transform to SQL statments
	// and fill in namedParams
	for (Map.Entry<String, String> param : filterParams.entrySet()) {
    	    String name = param.getKey().toLowerCase();
    	    String value = param.getValue();

    	    switch (name) {
	    case "elem_id":
	    case "elemid":
		name = "resource_id";
   	    break;
	    case "appid":
		name = "appId";
		break;
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
	    
	    q.append(String.format(" and %s=:%s", name, name));
	    namedParams.put(name, value);
    	}

	return makeQuery(q.toString(), namedParams, user, Event.class).getResultList();
    }

    public Event replace(Event oldEvent, Event newEvent) {
	newEvent.copyIdFrom(oldEvent);
	return entityManager.merge(newEvent);
    }
}

public interface EventRepository extends CrudRepository<Event, Long>,
					 EventRepositoryCustom {

    @Query("select new fi.hiit.dime.database.EventCount(actor, count(actor)) from Event e where user = ?1 group by actor order by count(actor) desc")
    List<EventCount> actorHistogram(User user);

    Event findOne(Long id);

    Event findOneByIdAndUser(Long id, User user);

    Event findOneByAppIdAndUser(String appId, User user);

    List<ResourcedEvent> findByTargettedResourceAndUser(InformationElement elem,
							User user);
    
    List<Event> findByUserOrderByStartDesc(User user, Pageable pageable);

    List<Event> findByUserOrderByStartDesc(User user);

    Long countByUser(User user);

    Long deleteByUser(User user);

    List<Event> findByUserAndStartIsAfterOrderByStartDesc(User user,
							  Date start);
}

