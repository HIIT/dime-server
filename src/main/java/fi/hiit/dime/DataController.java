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
import org.springframework.dao.InvalidDataAccessApiUsageException;
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
import java.util.Map;
import java.io.IOException;

/**
 * Controller for /data REST API, for writing and reading data objects. 
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
	    LOG.debug("JSON: " +
		     objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(input));
	} catch (IOException e) {
	    LOG.warn("IOException when trying to JSONify object: " + e);
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
    protected void eventLog(String eventName, User user, Event input, boolean dumpJson) {
	LOG.info("{} for user {} from {} at {}, with actor {}",
		 eventName, user.username, input.origin, new Date(), input.actor);
	if (dumpJson)
	    dumpJson(input);
    }

    /**
     * Helper method to log each information element uploaded.
     *
     * @param elemName  Name of information element class
     * @param user      User object
     * @param input     The information element that was uploaded
     * @param dumpJson  Whether to also print the JSON of the event object
     */
    protected void elementLog(String elemName, User user, InformationElement input,
			      boolean dumpJson) {
	LOG.info("{} for user {} at {}",
		 elemName, user.username, new Date());
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
    protected void eventLog(String eventName, User user, Event[] input, boolean dumpJson) {
	if (input.length > 0) {
	    LOG.info("{} for user {} from {} at {}, with actor {}",
		     eventName, user.username, input[0].origin, new Date(), input[0].actor);
	    if (dumpJson)
		dumpJson(input);
	}
    }

    /**
     * Helper method to log an array of uploaded information elements.
     *
     * @param elemName  Name of information element class
     * @param user      User object
     * @param input     The array of event objects that were uploaded
     * @param dumpJson  Whether to also print the JSON of the event object
     */
    protected void elementLog(String elemName, User user, InformationElement[] input,
			      boolean dumpJson) {
	if (input.length > 0) {
	    LOG.info("{} for user {} at {}",
		     elemName, user.username, new Date());
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
	expandInformationElement(InformationElement elem, User user) 
	throws NotFoundException, BadRequestException {
	if (elem == null)
	    return null;
	
	InformationElement expandedElem = null; 
	if (elem.getId() != null) {
	    expandedElem = infoElemDAO.findById(elem.getId(), user);

	    // Error if id doesn't exist 
	    if (expandedElem == null)
		throw new NotFoundException("id not found");
	    
	    // Check that appId is consistent (if given)
	    if (elem.appId != null && !elem.appId.equals(expandedElem.appId)) {
		LOG.error("appId not consistent: {} != {}", elem.appId, expandedElem.appId);
		throw new BadRequestException("appId not consistent");
	    }
	    
	} else if (elem.appId != null) {
	    InformationElement foo = infoElemDAO.findByAppId(elem.appId, user);
	    if (foo != null) {
		expandedElem = infoElemDAO.findById(foo.getId(), user);
		LOG.debug("appId given, expanded to id={}", expandedElem.getId());
	    } else {
		LOG.debug("appId given, unable to expand");
	    }
	}
	
	// If this is a stub element, expand it 
	if (elem.isStub()) {
	    if (expandedElem != null) {
		LOG.info("Expanded InformationElement for " + expandedElem.uri);
		// don't copy the text, takes too much space
		// expandedElem.plainTextContent = null; 
		return expandedElem;
	    } else {
		LOG.error("Uploaded stub, but unable to expand!");
		throw new BadRequestException("unable to expand stub");
	    }
	} else {
	    // If this is not a stub, but we found an existing
	    // element, replace it with the new one
	    if (expandedElem != null) {
		elem.user = user;
		elem = infoElemDAO.replace(expandedElem, elem);
	    } else {
		// Otherwise, this is just a new object, so store it
		elem.user = user;
		elem.autoFill();
	    }
	}

	return elem;
    }

    /**
     * Helper method to store an information element, and possibly expand its
     * content if needed.
     *
     * @param input InformationElement to store
     * @param user current authenticated user
     * @return The element as stored
     */
    private InformationElement storeElement(InformationElement elem, User user) 
	throws NotFoundException, BadRequestException {
	elem = expandInformationElement(elem, user);
	infoElemDAO.save(elem);
	return elem;
    }


    /**
     * Helper method to store an event, and possibly expand its
     * information element if needed.
     *
     * @param input Event to store
     * @param user current authenticated user
     * @return The event as stored
     */
    private Event storeEvent(Event input, User user) 
	throws NotFoundException, BadRequestException {
	input.user = user;

	if (input.getId() != null) {
	    if (eventDAO.findById(input.getId(), user) == null)
		throw new BadRequestException("Application not allowed to supply id.");
	}

	if (input instanceof ResourcedEvent) {
	    ResourcedEvent revent = (ResourcedEvent)input;
	    InformationElement elem = revent.targettedResource;
	    revent.targettedResource = storeElement(elem, user);
	}

	eventDAO.save(input);

	return input;
    }

    /** HTTP end point for uploading a single event. */    
    @RequestMapping(value="/event", method = RequestMethod.POST)
    public ResponseEntity<Event>
	event(Authentication auth, @RequestBody Event input)  
	throws NotFoundException, BadRequestException
    {
	User user = getUser(auth);

	input = storeEvent(input, user);

	eventLog("Event", user, input, true);

	return new ResponseEntity<Event>(input, HttpStatus.OK);
    }	

    /** HTTP end point for accessing single event. */    
    @RequestMapping(value="/event/{id}", method = RequestMethod.GET)
    public ResponseEntity<Event>
	event(Authentication auth, @PathVariable Long id) 
	throws NotFoundException
    {
	User user = getUser(auth);

	Event event = eventDAO.findById(id, user);

	if (event == null || !event.user.getId().equals(user.getId()))
	    throw new NotFoundException("Event not found");

	return new ResponseEntity<Event>(event, HttpStatus.OK);
    }	

    /** HTTP end point for uploading multiple events. */    
    @RequestMapping(value="/events", method = RequestMethod.POST)
    public ResponseEntity<Event[]>
	events(Authentication auth, @RequestBody Event[] input) 
	throws NotFoundException, BadRequestException
    {
	User user = getUser(auth);

	for (int i=0; i<input.length; i++) {
	    input[i] = storeEvent(input[i], user);
	}

	eventLog("Events", user, input, true);

	return new ResponseEntity<Event[]>(input, HttpStatus.OK);
    }	

    /** HTTP end point for accessing multiple events via a filtering
     * interface. */    
    @RequestMapping(value="/events", method = RequestMethod.GET)
    public ResponseEntity<Event[]>
	events(Authentication auth, @RequestParam Map<String, String> params) 
	throws BadRequestException
    {
	User user = getUser(auth);

	try {
	    List<Event> events = eventDAO.find(user.getId(), params);

	    Event[] eventsArray = new Event[events.size()];
	    events.toArray(eventsArray);	

	    return new ResponseEntity<Event[]>(eventsArray, HttpStatus.OK);
	} catch (IllegalArgumentException | InvalidDataAccessApiUsageException e) {
	    throw new BadRequestException("Invalid arguments");
	}
    }	

    /** HTTP end point for uploading a single information element. */    
    @RequestMapping(value="/informationelement", method = RequestMethod.POST)
    public ResponseEntity<InformationElement>
	informationElement(Authentication auth, @RequestBody InformationElement input)
	throws NotFoundException, BadRequestException
    {
	User user = getUser(auth);

	input = storeElement(input, user);

	elementLog("InformationElement", user, input, true);

	return new ResponseEntity<InformationElement>(input, HttpStatus.OK);
    }	

    /** HTTP end point for uploading multiple information elements. */    
    @RequestMapping(value="/informationelements", method = RequestMethod.POST)
    public ResponseEntity<InformationElement[]>
	informationElement(Authentication auth, @RequestBody InformationElement[] input) 
	throws NotFoundException, BadRequestException 
    {
	User user = getUser(auth);

	for (int i=0; i<input.length; i++) {
	    input[i] = storeElement(input[i], user);
	}

	elementLog("InformationElements", user, input, true);

	return new ResponseEntity<InformationElement[]>(input, HttpStatus.OK);
    }	

    /** HTTP end point for accessing a single informationelement. */    
    @RequestMapping(value="/informationelement/{id}", method = RequestMethod.GET)
    public ResponseEntity<InformationElement>
	informationElement(Authentication auth, @PathVariable Long id) 
	throws NotFoundException
    {
	User user = getUser(auth);

	InformationElement elem = infoElemDAO.findById(id, user);

	if (elem == null || !elem.user.getId().equals(user.getId()))
	    throw new NotFoundException("Element not found");

	return new ResponseEntity<InformationElement>(elem, HttpStatus.OK);
    }	

    /** HTTP end point for accessing multiple information elements via
     * a filtering interface. */    
    @RequestMapping(value="/informationelements", method = RequestMethod.GET)
    public ResponseEntity<InformationElement[]>
	informationElements(Authentication auth,
			    @RequestParam Map<String, String> params) 
	throws BadRequestException
    {
	User user = getUser(auth);

	try {
	    List<InformationElement> infoElems = infoElemDAO.find(user.getId(), params);

	    InformationElement[] infoElemsArray = new InformationElement[infoElems.size()];
	    infoElems.toArray(infoElemsArray);	

	    return new ResponseEntity<InformationElement[]>(infoElemsArray, HttpStatus.OK);
	} catch (IllegalArgumentException e) {
	    throw new BadRequestException("Invalid arguments");
	}
    }	

}
