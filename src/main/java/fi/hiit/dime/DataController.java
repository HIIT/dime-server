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

package fi.hiit.dime;

import fi.hiit.dime.authentication.User;
import fi.hiit.dime.authentication.CurrentUser;
import fi.hiit.dime.data.*;
import fi.hiit.dime.database.*;
import fi.hiit.dime.search.SearchIndex;
import static fi.hiit.dime.search.SearchIndex.weightType;

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
import org.springframework.transaction.annotation.Transactional;

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
    SearchIndex searchIndex;

    @Autowired 
    private ObjectMapper objectMapper;

    @Autowired
    DataController(EventDAO eventDAO,
                   InformationElementDAO infoElemDAO) {
        this.eventDAO = eventDAO;
        this.infoElemDAO = infoElemDAO;
    }

    private String dumpJson(Object input) {
        try {
            return objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(input);
        } catch (IOException e) {
            return "Unable to parse JSON object.";
        }
    }

    /**
     * Helper method to log each event uploaded.
     *
     * @param user      User object
     * @param input     The event object that was uploaded
     * @param dumpJson  Whether to also print the JSON of the event object
     */
    protected void eventLog(User user, Event input, boolean dumpJson) {
        LOG.info("{} for user {} from {} at {}, with actor {}",
                 input.getClass().getSimpleName(), user.username,
                 input.origin, new Date(), input.actor);
        if (dumpJson)
            LOG.debug(dumpJson(input));
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
            LOG.debug(dumpJson(input));
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
                LOG.debug(dumpJson(input));
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
    @Transactional
    protected InformationElement 
        expandInformationElement(InformationElement elem, User user) 
        throws NotFoundException, BadRequestException {
        if (elem == null)
            return null;
        
        InformationElement oldElem = null; 
        if (elem.getId() != null) {
            oldElem = infoElemDAO.findById(elem.getId(), user);

            // Error if id doesn't exist 
            if (oldElem == null)
                throw new NotFoundException("id not found");
            
            // Check that appId is consistent (if given)
            if (elem.appId != null && !elem.appId.equals(oldElem.appId)) {
                LOG.error("appId not consistent: {} != {}", elem.appId, oldElem.appId);
                throw new BadRequestException("appId not consistent");
            }
            
        } else if (elem.appId != null) {
            oldElem = infoElemDAO.findByAppId(elem.appId, user);
            if (oldElem != null)
                LOG.debug("appId given, expanded to id={}",
                          oldElem.getId());
        }
        
        // If this is a stub element, expand it 
        if (elem.isStub()) {
            if (oldElem != null) {
                LOG.info("Expanded InformationElement for " + oldElem.uri);
                // don't copy the text, takes too much space
                // oldElem.plainTextContent = null; 
                return oldElem;
            } else {
                LOG.error("Uploaded stub, but unable to expand!");
                LOG.error(dumpJson(elem));
                throw new BadRequestException("unable to expand stub");
            }
        } else {
            // If this is not a stub, but we found an existing
            // element, replace it with the new one
            if (oldElem != null) {
                // if the classes are not the same
                if (!elem.getClass().equals(oldElem.getClass())) {
                    String msg = 
                        String.format("Type (%s) incompatible with existing " +
                                      "object (%s) with the same %s.", 
                                      elem.getClass().getName(),
                                      oldElem.getClass().getName(),
                                      elem.getId() == null ? "appId" : "id");
                    throw new BadRequestException(msg);
                }

                elem.user = user;
                elem = infoElemDAO.replace(oldElem, elem);
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
    @Transactional
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
    @Transactional
    private Event storeEvent(Event event, User user) 
        throws NotFoundException, BadRequestException {

        // FIXME: should be unified with expandInformationElement code
        Event expandedEvent = null; 
        if (event.getId() != null) {
            expandedEvent = eventDAO.findById(event.getId(), user);

            // Error if id doesn't exist 
            if (expandedEvent == null)
                throw new NotFoundException("id not found");
            
            // Check that appId is consistent (if given)
            if (event.appId != null && !event.appId.equals(expandedEvent.appId)) {
                LOG.error("appId not consistent: {} != {}", event.appId, expandedEvent.appId);
                throw new BadRequestException("appId not consistent");
            }
            
        } else if (event.appId != null) {
            expandedEvent = eventDAO.findByAppId(event.appId, user);
            if (expandedEvent != null)
                LOG.debug("appId given, expanded to id={}",
                          expandedEvent.getId());
        }

        if (event instanceof ResourcedEvent) {
            ResourcedEvent revent = (ResourcedEvent)event;
            InformationElement elem = revent.targettedResource;
            revent.targettedResource = storeElement(elem, user);
        }

        if (expandedEvent != null) {
            event.user = user;
            event.autoFill();
            event = eventDAO.replace(expandedEvent, event);
        } else {
            // Otherwise, this is just a new object, so store it
            event.user = user;
            event.autoFill();
        }
        eventDAO.save(event);

        return event;
    }

    /**
       @apiDefine user User access 
       You need to be authenticated as a registered DiMe user.
    */

    /** HTTP end point for uploading a single event. 
        @api {post} /data/event/ Upload single event
        @apiName PostEvent
        @apiDescription Upload a new event as a JSON object.  For the data types, see <a href="https://github.com/HIIT/dime-server/wiki/Data">the Data page in the wiki</a>. 

On success, the response will be the uploaded object with some fields like the id filled in.

A <a href="https://github.com/HIIT/dime-server/blob/master/scripts/logger-example.py">full working example</a> of uploading an event can be found in the git repository.
        
        @apiExample {json} Example of JSON to upload
            {
                "@type": "SearchEvent",
                "actor": "My example logger",
                "query": "Some search query"
            }

        @apiSuccessExample {json} Example successful response:
            HTTP/1.1 200 OK
            {
                "@type": "SearchEvent",
                "actor": "My example logger",
                "duration": 0.0,
                "end": 1463384282690,
                "id": 1234,
                "start": 1463384282690,
                "tags": [],
                "query": "Some search query"
                "user": {
                    "id": 3,
                    "role": "USER",
                    "username": "testuser"
                }
            }
        @apiPermission user
        @apiGroup Events
        @apiVersion 0.1.2
    */
    @RequestMapping(value="/event", method = RequestMethod.POST)
    public ResponseEntity<Event>
        event(Authentication auth, @RequestBody Event input)  
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        input = storeEvent(input, user);

        eventLog(user, input, true);

        return new ResponseEntity<Event>(input, HttpStatus.OK);
    }   

    /** HTTP end point for accessing single event. 

        @api {get} /data/event/:id Access single event
        @apiName GetEvent
        @apiParam {Number} id Event's unique ID
        @apiDescription On success the response will be the event with the given id in JSON format. For the data types, see <a href="https://github.com/HIIT/dime-server/wiki/Data">https://github.com/HIIT/dime-server/wiki/Data</a>.
        @apiSuccessExample {json} Example successful response:
            HTTP/1.1 200 OK
            {
                "@type": "DesktopEvent",
                "actor": "DiMe browser extension",
                "duration": 0.0,
                "end": 1463384282690,
                "id": 1784,
                "origin": "0:0:0:0:0:0:0:1",
                "start": 1463384282690,
                "tags": [],
                "targettedResource": {
                    "@type": "Document",
                    "id": 1775,
                    "isStoredAs": "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo/#RemoteDataObject",
                    "mimeType": "application/json",
                    "plainTextContent": "Hello, world",
                    "tags": [
                        {
                            "@type": "Tag",
                            "text": "hello"
                        },
                        {
                            "@type": "Tag",
                            "text": "world"
                        }
                    ],
                    "timeCreated": 1463384282789,
                    "timeModified": 1463384282789,
                    "title": "Hello, world",
                    "type": "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo/#PlainTextDocument",
                    "uri": "http://example.com",
                    "user": {
                        "id": 3,
                        "role": "USER",
                        "username": "testuser"
                    }
                },
                "timeCreated": 1463384282803,
                "timeModified": 1463384282803,
                "type": "http://www.semanticdesktop.org/ontologies/2010/01/25/nuao/#UsageEvent",
                "user": {
                    "id": 3,
                    "role": "USER",
                    "username": "testuser"
                }
            }

        @apiErrorExample {json} Example error response:
            HTTP/1.1 404 Not Found
            {
                "error": "Not Found",
                "exception": "fi.hiit.dime.AuthorizedController$NotFoundException",
                "message": "Event not found",
                "path": "/api/data/event/12345",
                "status": 404,
                "timestamp": 1466580641725
            }

        @apiPermission user
        @apiGroup Events
        @apiVersion 0.1.2
     */
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

    /** HTTP end point for deleting single event. 

        @api {delete} /data/event/:id Delete single event
        @apiName DeleteEvent
        @apiParam {Number} id Event's unique ID
        @apiDescription On success, the response will be an empty HTTP 204.

        @apiPermission user
        @apiGroup Events
        @apiVersion 0.1.2
     */
    @RequestMapping(value="/event/{id}", method = RequestMethod.DELETE)
    public ResponseEntity eventDelete(Authentication auth, @PathVariable Long id) 
        throws NotFoundException
    {
        User user = getUser(auth);

        try {
            if (!eventDAO.remove(id, user))
                throw new NotFoundException("Event not found");
        } catch (Exception e) {
            return new ResponseEntity(HttpStatus.INTERNAL_SERVER_ERROR);
        }
        return new ResponseEntity(HttpStatus.NO_CONTENT);
    }

    /** HTTP end point for uploading multiple events. 

        @api {post} /data/events/ Upload list of events
        @apiName PostEvents
        @apiDescription Upload several events in one request, specified as a JSON list.

        @apiExample {json} Example of JSON to upload
            [
                {
                    "@type": "SearchEvent",
                    "actor": "My example logger",
                    "query": "Some search query"
                },
                {
                    "@type": "SearchEvent",
                    "actor": "My example logger",
                    "query": "Some other query"
                }
            ]

        @apiPermission user
        @apiGroup Events
        @apiVersion 0.1.2
     */    
    @RequestMapping(value="/events", method = RequestMethod.POST)
    public ResponseEntity<Event[]>
        events(Authentication auth, @RequestBody Event[] input) 
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        for (int i=0; i<input.length; i++) {
            input[i] = storeEvent(input[i], user);
            eventLog(user, input[i], true);
        }

        return new ResponseEntity<Event[]>(input, HttpStatus.OK);
    }   

    /** HTTP end point for accessing multiple events via a filtering
        interface.

        @api {get} /data/events/ Access multiple events
        @apiName GetEvents
        @apiDescription Access events through filtering with parameters.

        @apiParam (Filtering) {String} [appid] appId to match (exactly)
        @apiParam (Filtering) {String} [elemid] the numeric id of the
        related information element
        @apiParam (Filtering) {String} [actor] match actor field 
        @apiParam (Filtering) {String} [origin] match origin field
        @apiParam (Filtering) {String} [type] match type field
        @apiParam (Filtering) {String} [query] match query field
        @apiParam (Filtering) {String} [tag] exact tag matching (just
        one tag needs to match)
        @apiParam (Filtering) {DateTime} [after] matches events
        occurring after this time stamp, the time stamp format is the
        same as for the start and end properties of the Data objects
        @apiParam (Filtering) {DateTime} [before] matches events
        occurring before this time stamp (can be combined with after
        to get a time interval)

        @apiParam (Options) {Boolean} [includePlainTextContent] set to
        'true' if you wish to include the plainTextContent of the
        InformationElements linked to the Events (these are normally
        removed to reduce verbosity)

        @apiPermission user
        @apiGroup Events
        @apiVersion 0.1.2

     */    
    @RequestMapping(value="/events", method = RequestMethod.GET)
    public ResponseEntity<Event[]>
        events(Authentication auth, 
               @RequestParam(value="includePlainTextContent", required=false,
                             defaultValue="false") Boolean includePlainTextContent,
               @RequestParam Map<String, String> params) 
        throws BadRequestException
    {
        User user = getUser(auth);

        // remove includePlainTextContent from map since we capture
        // this separately
        if (params.containsKey("includePlainTextContent"))
            params.remove("includePlainTextContent");

        try {
            List<Event> events = eventDAO.find(user.getId(), params);

            // We remove plainTextContents of linked
            // InformationElements to reduce verbosity
            if (!includePlainTextContent) {
                for (Event e : events)
                    if (e instanceof ResourcedEvent)
                        ((ResourcedEvent)e).targettedResource.plainTextContent = null;
            }

            Event[] eventsArray = new Event[events.size()];
            events.toArray(eventsArray);        

            return new ResponseEntity<Event[]>(eventsArray, HttpStatus.OK);
        } catch (IllegalArgumentException | InvalidDataAccessApiUsageException e) {
            throw new BadRequestException("Invalid arguments: " + e);
        }
    }   

    /** HTTP end point for uploading a single information element. */    
    @RequestMapping(value="/informationelement", method = RequestMethod.POST)
    public ResponseEntity<InformationElement>
        informationElement(Authentication auth, 
                           @RequestBody InformationElement input)
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
    @RequestMapping(value="/informationelement/{id}",
                    method = RequestMethod.GET)
    public ResponseEntity<InformationElement>
        informationElement(Authentication auth, 
                           @PathVariable Long id,
                           @RequestParam(defaultValue="") String keywords)
        throws NotFoundException
    {
        User user = getUser(auth);

        InformationElement elem = infoElemDAO.findById(id, user);

        if (elem == null || !elem.user.getId().equals(user.getId()))
            throw new NotFoundException("Element not found");

        if (!keywords.isEmpty()) {
            searchIndex.updateIndex();
            elem.weightedKeywords =
                searchIndex.getKeywords(elem, weightType(keywords));
        }

        return new ResponseEntity<InformationElement>(elem, HttpStatus.OK);
    }   

    /** HTTP end point for deleting single information element. */
    @RequestMapping(value="/informationelement/{id}",
                    method = RequestMethod.DELETE)
    public ResponseEntity informationElementDelete(Authentication auth, 
                                                   @PathVariable Long id) 
        throws NotFoundException
    {
        User user = getUser(auth);

        try {
            if (!infoElemDAO.remove(id, user))
                throw new NotFoundException("Element not found");
        } catch (Exception e) {
            return new ResponseEntity(HttpStatus.INTERNAL_SERVER_ERROR);
        }
        return new ResponseEntity(HttpStatus.NO_CONTENT);
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
            List<InformationElement> infoElems = 
                infoElemDAO.find(user.getId(), params);

            InformationElement[] infoElemsArray = 
                new InformationElement[infoElems.size()];
            infoElems.toArray(infoElemsArray);  

            return new ResponseEntity<InformationElement[]>(infoElemsArray, 
                                                            HttpStatus.OK);
        } catch (IllegalArgumentException e) {
            throw new BadRequestException("Invalid arguments");
        }
    }

    /** 
        Helper method to save a generic DiMeData object.
    */
    protected void saveData(DiMeData obj) {
        if (obj instanceof InformationElement)
            infoElemDAO.save((InformationElement)obj);
        else if (obj instanceof Event)
            eventDAO.save((Event)obj);
    }

    /**
       Helper method to add a tag to a DiMeData object, with sanity
       checks.
    */
    protected <T extends DiMeData> T addTag(User user, T obj, Tag tag)
        throws NotFoundException
    {
        if (obj == null || !obj.user.getId().equals(user.getId()))
            throw new NotFoundException("Object not found");

        obj.addTag(tag);
        saveData(obj);

        return obj;
    }

    /**
       Helper method to add a list of tags to a DiMeData object, with
       sanity checks.
    */
    protected <T extends DiMeData> T addTags(User user, T obj, Tag[] tags)
        throws NotFoundException
    {
        if (obj == null || !obj.user.getId().equals(user.getId()))
            throw new NotFoundException("Object not found");

        for (int i=0; i<tags.length; i++)
            obj.addTag(tags[i]);

        saveData(obj);

        return obj;
    }

    /**
       Helper method to remove a tag from a DiMeData object, with
       sanity checks.
    */
    protected <T extends DiMeData> T removeTag(User user, T obj, Tag tag) 
        throws NotFoundException
    {
        if (obj == null || !obj.user.getId().equals(user.getId()))
            throw new NotFoundException("Object not found");

        obj.removeTag(tag.text);

        saveData(obj);

        return obj;
    }

    /** HTTP end point for adding a tag to an Information Element. */    
    @RequestMapping(value="/informationelement/{id}/addtag", 
                    method = RequestMethod.POST)
    public ResponseEntity<InformationElement>
        addTag(Authentication auth, @PathVariable Long id,
               @RequestBody Tag input) 
        throws NotFoundException
    {
        User user = getUser(auth);
        InformationElement elem =
            addTag(user, infoElemDAO.findById(id, user), input);
        return new ResponseEntity<InformationElement>(elem, HttpStatus.OK);
    }   

    /** HTTP end point for adding several tags to an Information Element. */    
    @RequestMapping(value="/informationelement/{id}/addtags", 
                    method = RequestMethod.POST)
    public ResponseEntity<InformationElement>
        addTags(Authentication auth, @PathVariable Long id,
               @RequestBody Tag[] input) 
        throws NotFoundException
    {
        User user = getUser(auth);
        InformationElement elem =
            addTags(user, infoElemDAO.findById(id, user), input);
        return new ResponseEntity<InformationElement>(elem, HttpStatus.OK);
    }   

    /** HTTP end point for removing a tag from an Information Element. */    
    @RequestMapping(value="/informationelement/{id}/removetag", 
                    method = RequestMethod.POST)
    public ResponseEntity<InformationElement>
        removeTag(Authentication auth, @PathVariable Long id,
                  @RequestBody Tag input) 
        throws NotFoundException
    {
        User user = getUser(auth);
        InformationElement elem =
            removeTag(user, infoElemDAO.findById(id, user), input);
        return new ResponseEntity<InformationElement>(elem, HttpStatus.OK);
    }   

    /** HTTP end point for adding a tag to an Event. */    
    @RequestMapping(value="/event/{id}/addtag", method = RequestMethod.POST)
    public ResponseEntity<Event>
        eventAddTag(Authentication auth, @PathVariable Long id,
                    @RequestBody Tag input) 
        throws NotFoundException
    {
        User user = getUser(auth);
        Event event = addTag(user, eventDAO.findById(id, user), input);
        return new ResponseEntity<Event>(event, HttpStatus.OK);
    }   

    /** HTTP end point for adding several tags to an Information Element. */    
    @RequestMapping(value="/event/{id}/addtags", 
                    method = RequestMethod.POST)
    public ResponseEntity<Event>
        eventAddTags(Authentication auth, @PathVariable Long id,
                     @RequestBody Tag[] input) 
        throws NotFoundException
    {
        User user = getUser(auth);
        Event event = addTags(user, eventDAO.findById(id, user), input);
        return new ResponseEntity<Event>(event, HttpStatus.OK);
    }   

    /** HTTP end point for removing a tag from an Information Element. */    
    @RequestMapping(value="/event/{id}/removetag", 
                    method = RequestMethod.POST)
    public ResponseEntity<Event>
        eventRemoveTag(Authentication auth, @PathVariable Long id,
                       @RequestBody Tag input) 
        throws NotFoundException
    {
        User user = getUser(auth);
        Event event = removeTag(user, eventDAO.findById(id, user), input);
        return new ResponseEntity<Event>(event, HttpStatus.OK);
    }   
}
