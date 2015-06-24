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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

import java.util.Date;
import java.util.List;

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
    DataController(EventDAO eventDAO,
    		   InformationElementDAO infoElemDAO) {
    	this.eventDAO = eventDAO;
    	this.infoElemDAO = infoElemDAO;
    }

    /**
     * Helper method to log each event uploaded.
     *
     * @param eventName Name of event class
     * @param user      User object
     * @param input     The event object that was uploaded
     */
    protected void eventLog(String eventName, User user, Event input) {
	LOG.info("{} for user {} from {} at {}, with actor {}",
		 eventName, user.username, input.origin, new Date(), input.actor);
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
		    msg.plainTextContent = msg.subject + "\n\n" + msg.plainTextContent;
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
     * @api {post} /data/searchevent Upload SearchEvent
     * @apiName PostSearchEvent
     * @apiGroup Data
     * 
     * @apiParam {Object} - <code>SearchEvent</code> object to upload

     * @apiSuccess {Object} - Returns the added object, possibly with
     *     some additional fields filled in such as the unique id.
     */
    @RequestMapping(value="/searchevent", method = RequestMethod.POST)
    public ResponseEntity<SearchEvent> searchEvent(Authentication auth, 
						   @RequestBody SearchEvent input) {
	User user = getUser(auth);
	input.user = user;

	eventDAO.save(input);

	eventLog("SearchEvent", user, input);
	return new ResponseEntity<SearchEvent>(input, HttpStatus.OK);
    }

    /**
     * @api {post} /data/desktopevent Upload DesktopEvent
     * @apiName PostDesktopEvent
     * @apiGroup Data
     * 
     * @apiParam {Object} - <code>DesktopEvent</code> object to upload

     * @apiSuccess {Object} - Returns the added object, possibly with
     *     some additional fields filled in such as the unique id.
     */
    @RequestMapping(value="/desktopevent", method = RequestMethod.POST)
    public ResponseEntity<DesktopEvent> 
	documentEvent(Authentication auth, @RequestBody DesktopEvent input) {
	User user = getUser(auth);
	input.user = user;
	input.targettedResource = 
	    expandInformationElement(input.targettedResource, user);

	eventDAO.save(input);
	
	eventLog("DesktopEvent", user, input);
	return new ResponseEntity<DesktopEvent>(input, HttpStatus.OK);
    }

    /**
     * @api {post} /data/feedbackevent Upload FeedbackEvent
     * @apiName PostFeedbackEvent
     * @apiGroup Data
     * 
     * @apiParam {Object} - <code>FeedbackEvent</code> object to upload

     * @apiSuccess {Object} - Returns the added object, possibly with
     *     some additional fields filled in such as the unique id.
     */
    @RequestMapping(value="/feedbackevent", method = RequestMethod.POST)
    public ResponseEntity<FeedbackEvent> 
	documentEvent(Authentication auth, @RequestBody FeedbackEvent input) {
	User user = getUser(auth);
	input.user = user;
	input.targettedResource = 
	    expandInformationElement(input.targettedResource, user);

	eventDAO.save(input);
	
	eventLog("FeedbackEvent", user, input);
	return new ResponseEntity<FeedbackEvent>(input, HttpStatus.OK);
    }

    /**
     * @api {post} /data/messageevent Upload MessageEvent
     * @apiName PostMessageEvent
     * @apiGroup Data
     * 
     * @apiParam {Object} - <code>MessageEvent</code> object to upload

     * @apiSuccess {Object} - Returns the added object, possibly with
     *     some additional fields filled in such as the unique id.
     */
    @RequestMapping(value="/messageevent", method = RequestMethod.POST)
    public ResponseEntity<MessageEvent> 
	messageEvent(Authentication auth, @RequestBody MessageEvent input) {
	User user = getUser(auth);
	input.user = user;

	input.targettedResource = expandMessage(input.targettedResource, user);

	eventDAO.save(input);
	
	eventLog("MessageEvent", user, input);
	return new ResponseEntity<MessageEvent>(input, HttpStatus.OK);
    }

    /**
     * @api {get} /data/informationelement Get InformationElements
     * @apiName GetInformationElement
     * @apiGroup Read
     * 
     * @apiSuccess {Object[]} - Array of InformationElement objects
     */
    @RequestMapping(value="/informationelement", method = RequestMethod.GET)
    public ResponseEntity<List<InformationElement>> 
	informationElement(Authentication auth) {
	User user = getUser(auth);

	List<InformationElement> results = infoElemDAO.elementsForUser(user.id);

	return new ResponseEntity<List<InformationElement>>(results, HttpStatus.OK);
    }
    
}
