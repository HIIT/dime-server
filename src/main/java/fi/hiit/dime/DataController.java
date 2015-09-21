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

package fi.hiit.dime;

import fi.hiit.dime.authentication.User;
import fi.hiit.dime.authentication.CurrentUser;
import fi.hiit.dime.data.*;
import fi.hiit.dime.database.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Date;
import java.util.List;
import java.util.Properties;
import java.io.IOException;

/**
 * Controller for /data REST API, for writing and reading data objects. 
 *
 * Each new object type needs its own endpoint here. The convention is
 * to name the endpoint as the class but in lower case, e.g. for
 * <code>SearchEvent</code> the REST endpoint is
 * <code>/data/searchevent</code>.
 *
 * @author Mats Sjöberg (mats.sjoberg@helsinki.fi)
 */
@RestController
@RequestMapping("/api/data")
public class DataController extends AuthorizedController {
    private static final Logger LOG = 
	LoggerFactory.getLogger(DataController.class);

    private final EventDAO eventDAO;
    private final InformationElementDAO infoElemDAO;

    @Autowired 
    private ObjectMapper objectMapper;

    @Autowired
    DataController(EventDAO eventDAO,
    		   InformationElementDAO infoElemDAO) {
    	this.eventDAO = eventDAO;
    	this.infoElemDAO = infoElemDAO;
    }

    private void dumpJson(Object input) {
	try {
	    LOG.info("JSON: " +
		     objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(input));
	} catch (IOException e) {
	}
    }

    /**
     * Helper method to log each event uploaded.
     *
     * @param eventName Name of event class
     * @param user      User object
     * @param input     The event object that was uploaded
     * @param dumpJson  Whether to also print the JSON of the event object
     */
    protected void eventLog(String  eventName, User user, Event input, Boolean dumpJson) {
	LOG.info("{} for user {} from {} at {}, with actor {}",
		 eventName, user.username, input.origin, new Date(), input.actor);
	if (dumpJson)
	    dumpJson(input);
    }

    /**
     * Helper method to log an array of uploaded events.
     *
     * @param eventName Name of event class
     * @param user      User object
     * @param input     The array of event objects that were uploaded
     * @param dumpJson  Whether to also print the JSON of the event object
     */
    protected void eventLog(String eventName, User user, Event[] input, Boolean dumpJson) {
	if (input.length > 0) {
	    LOG.info("{} for user {} from {} at {}, with actor {}",
		     eventName, user.username, input[0].origin, new Date(), input[0].actor);
	    if (dumpJson)
		dumpJson(input);
	}
    }

    /**
     * Helper method to expand stub InformationElement objects.
     *
     * Stub objects are those which only include the id with the
     * assumption that the original full object already exists in the
     * database.
     *
     * @param elem InformationElement to expand
     * @param user current authenticated user
     * @return The expanded InformationElement
     */
    protected InformationElement 
	expandInformationElement(InformationElement elem, User user) {
	if (elem != null) {
	    if (!elem.isStub()) {
		elem.user = user;
		infoElemDAO.save(elem);
	    } else { // expand if only a stub elem was included
		InformationElement expandedElem = infoElemDAO.findById(elem.id);	
		if (expandedElem != null) {
		    LOG.info("Expanded InformationElement for " + expandedElem.uri);
		    // don't copy the text, takes too much space
		    expandedElem.plainTextContent = null; 
		    elem = expandedElem;
		}
	    }
	} 
	return elem;
    }

    /**
     * Helper method to expand stub Message objects.
     *
     * Stub objects are those which only include the id with the
     * assumption that the original full object already exists in the
     * database.
     *
     * @param msg Message to expand
     * @param user current authenticated user
     * @return The expanded Message
     */
    protected Message expandMessage(Message msg, User user) {
	if (msg != null) {
	    if (!msg.isStub()) {
		msg.user = user;
		if (msg.subject.length() > 0)
		    msg.plainTextContent = 
			msg.subject + "\n\n" + msg.plainTextContent;
		infoElemDAO.save(msg);

		// infoElemDAO.save(msg.from);

		// for (Person to : msg.to)
		//     infoElemDAO.save(to);

		// for (Person cc : msg.cc)
		//     infoElemDAO.save(cc);

	    } else { // expand if only a stub msg was included
		Message expandedMsg = (Message)infoElemDAO.findById(msg.id);	
		if (expandedMsg != null) {
		    LOG.info("Expanded Message for " + expandedMsg.uri);
		    // don't copy the text, takes too much space
		    expandedMsg.plainTextContent = null; 
		    msg = expandedMsg;
		}
	    }
	} 

	return msg;
    }

    /**
     * Helper method to store an event, and possibly expand its
     * information element if needed.
     *
     * @param input Event to store
     * @param user current authenticated user
     * @return The event as stored
     */
    private Event storeEvent(Event input, User user) {
	input.user = user;

	if (input instanceof ResourcedEvent) {
	    ResourcedEvent revent = (ResourcedEvent)input;
	    InformationElement elem = revent.targettedResource;

	    if (elem instanceof Message)
		elem = expandMessage((Message)elem, user);
	    else
		elem = expandInformationElement(elem, user);

	    revent.targettedResource = elem;
	}
	eventDAO.save(input);

	return input;
    }

    /** HTTP end point for uploading a single event. */    
    @RequestMapping(value="/event", method = RequestMethod.POST)
    public ResponseEntity<Event>
	event(Authentication auth, @RequestBody Event input) {
	User user = getUser(auth);

	input = storeEvent(input, user);

	eventLog("Event", user, input, true);

	return new ResponseEntity<Event>(input, HttpStatus.OK);
    }	

    /** HTTP end point for accessing single event. */    
    @RequestMapping(value="/event/{id}", method = RequestMethod.GET)
    public ResponseEntity<Event>
	event(Authentication auth, @PathVariable String id) {
	User user = getUser(auth);

	Event event = eventDAO.findById(id);

	if (event == null)
	    return new ResponseEntity<Event>(HttpStatus.NOT_FOUND);

	if (!event.user.id.equals(user.id))
	    return new ResponseEntity<Event>(HttpStatus.UNAUTHORIZED);

	return new ResponseEntity<Event>(event, HttpStatus.OK);
    }	

    /** HTTP end point for uploading multiple events. */    
    @RequestMapping(value="/events", method = RequestMethod.POST)
    public ResponseEntity<Event[]>
	events(Authentication auth, @RequestBody Event[] input) {
	User user = getUser(auth);

	for (int i=0; i<input.length; i++) {
	    input[i] = storeEvent(input[i], user);
	}

	eventLog("Events", user, input, true);

	return new ResponseEntity<Event[]>(input, HttpStatus.OK);
    }	

    /** HTTP end point for accessing multiple events via a search-like
     * interface. */    
    @RequestMapping(value="/events", method = RequestMethod.GET)
    public ResponseEntity<Event[]>
	events(Authentication auth, 
	       @RequestParam String actor) {
	User user = getUser(auth);

	Properties searchProps = new Properties();
	if (actor != null)
	    searchProps.setProperty("actor", actor);

	List<Event> events = eventDAO.find(user.id, searchProps);

	Event[] eventsArray = new Event[events.size()];
	events.toArray(eventsArray);	

	return new ResponseEntity<Event[]>(eventsArray, HttpStatus.OK);
    }	

    /** HTTP end point for uploading a single informationelement. */    
    @RequestMapping(value="/informationelement", method = RequestMethod.GET)
    public ResponseEntity<List<InformationElement>> 
    	informationElement(Authentication auth) {
    	User user = getUser(auth);

    	List<InformationElement> results = infoElemDAO.elementsForUser(user.id);

    	return new ResponseEntity<List<InformationElement>>(results, HttpStatus.OK);
    }

    /** HTTP end point for accessing a single informationelement. */    
    @RequestMapping(value="/informationelement/{id}", method = RequestMethod.GET)
    public ResponseEntity<InformationElement>
	informationElement(Authentication auth, @PathVariable String id) {
	User user = getUser(auth);

	InformationElement elem = infoElemDAO.findById(id);

	if (elem == null)
	    return new ResponseEntity<InformationElement>(HttpStatus.NOT_FOUND);

	if (!elem.user.id.equals(user.id))
	    return new ResponseEntity<InformationElement>(HttpStatus.UNAUTHORIZED);

	return new ResponseEntity<InformationElement>(elem, HttpStatus.OK);
    }	

}
