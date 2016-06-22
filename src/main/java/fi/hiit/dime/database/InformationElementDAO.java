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
import fi.hiit.dime.data.InformationElement;
import fi.hiit.dime.data.ResourcedEvent;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class InformationElementDAO 
    extends DiMeDAO<InformationElement, InfoElemRepository> {

    @Autowired
    private EventDAO eventDAO;

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


    /**
       Removes a single item.

       @param id Item id
       @param user User
       @return True if it was deleted, false otherwise.
    */
    @Override
    @Transactional
    public boolean remove(Long id, User user) {
        InformationElement elem = findById(id, user);
    
        List<ResourcedEvent> events = eventDAO.findByElement(elem, user);

        for (ResourcedEvent e : events) {
            eventDAO.remove(e.getId(), user);
        }

        return super.remove(id, user);
    }

}

