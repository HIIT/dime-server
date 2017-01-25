/*
  Copyright (c) 2015-2016 University of Helsinki

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

import fi.hiit.dime.authentication.User;
import fi.hiit.dime.data.Event;
import fi.hiit.dime.data.InformationElement;
import fi.hiit.dime.data.IntentModelFeedbackEvent;
import fi.hiit.dime.data.Profile;
import fi.hiit.dime.data.ResourcedEvent;

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

class EventRepositoryImpl extends DiMeRepositoryImpl<Event> {
    @Override
        public List<Event> find(User user, Map<String, String> filterParams,
                                int page, int limit, String order, boolean desc) {
        // We build the SQL query into q
        StringBuilder q = new StringBuilder("select e from Event e " +
                                            "where e.user.id=:userId");

        // Map for storing named parameters for the query we are
        // constructing
        Map<String, Object> namedParams = new HashMap<String, Object>();

        // Loop over user's parameters, and transform to SQL statments
        // and fill in namedParams
        for (Map.Entry<String, String> param : filterParams.entrySet()) {
            String name = param.getKey().toLowerCase();
            String value = param.getValue();

            String criteria = "";

            switch (name) {
            case "tag":
                criteria = "(select count(*) from e.tags where text=:tag) > 0";
                break;
            case "after":
                criteria = "start >= :after";
                namedParams.put(name, parseDateForQuery(value));
                value = null;
                break;
            case "before":
                criteria = "e.end <= :before";
                namedParams.put(name, parseDateForQuery(value));
                value = null;
                break;
            case "elem_id":
            case "elemid":
                name = "resource_id";
            break;
            case "appid":
                name = "appId";
                break;
            case "sessionid":
                name = "sessionId";
                break;
            case "actor":
            case "origin":
            case "type":
            case "query":
                // case "":
                break;
            default:
                throw new IllegalArgumentException(name);
            }

            if (criteria.isEmpty())
                criteria = String.format("%s=:%s", name, name);

            q.append(" and " + criteria);
            if (value != null)
                namedParams.put(name, value);
        }

        if (order != null) {
            switch (order) {
            case "start":
            case "end":
                q.append(" order by " + order);
                if (desc)
                    q.append(" desc");
                else
                    q.append(" asc");
                break;
            default:
                throw new IllegalArgumentException(order);
            }
        }            

        return makeQuery(q.toString(), namedParams, page, limit, user,
                         Event.class).getResultList();
    }
}

public interface EventRepository extends DiMeRepository<Event> {

    @Query("select new fi.hiit.dime.database.EventCount(actor, count(actor)) from Event e where user = ?1 group by actor order by count(actor) desc")
    List<EventCount> actorHistogram(User user);

    List<ResourcedEvent> findByTargettedResourceAndUser(InformationElement elem,
                                                        User user);

    List<IntentModelFeedbackEvent> findByRelatedProfileAndUser(Profile profile,
                                                               User user);

    List<Event> findByUserOrderByStartDesc(User user, Pageable pageable);

    List<Event> findByUserOrderByStartDesc(User user);

    List<Event> findByUserAndTimeModifiedIsAfterOrderByStartDesc(User user,
                                                                 Date start);
}
