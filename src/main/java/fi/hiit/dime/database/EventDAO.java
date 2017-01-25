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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.Iterator;
import java.util.List;

@Service
public class EventDAO extends DiMeDAO<Event, EventRepository> {
    private static final Logger LOG = LoggerFactory.getLogger(EventDAO.class);

    @Transactional(readOnly = true)
    public List<ResourcedEvent> findByElement(InformationElement elem, User user) {
        return repo.findByTargettedResourceAndUser(elem, user);
    }

    @Transactional(readOnly = true)
    public List<IntentModelFeedbackEvent> findByRelatedProfile(Profile profile, 
                                                               User user) {
        return repo.findByRelatedProfileAndUser(profile, user);
    }

    @Transactional(readOnly = true)
    public List<Event> eventsForUser(Long userId, int limit) {
        return repo.findByUserOrderByStartDesc(User.makeUser(userId),
                                               new PageRequest(0, limit));
    }

    @Transactional(readOnly = true)
    public List<Event> eventsSince(Long userId, Date since) {
        return repo.findByUserAndTimeModifiedIsAfterOrderByStartDesc(User.makeUser(userId), since);
    }

    public List<EventCount> getActorHistogram(Long userId) {
        List<EventCount> hist = repo.actorHistogram(User.makeUser(userId));

        // filter list a bit ...
        long totCount = 0;
        for (Iterator<EventCount> it = hist.iterator(); it.hasNext(); ) {
            EventCount ec = it.next();
            if (ec.value == null || ec.count == 0)
                it.remove();
            else
                totCount += ec.count;
        }

        for (EventCount ec : hist)
            ec.perc = ec.count/(double)totCount*100.0;

        return hist;
    }    
}
