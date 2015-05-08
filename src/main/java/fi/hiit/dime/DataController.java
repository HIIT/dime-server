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

//------------------------------------------------------------------------------

import fi.hiit.dime.authentication.CurrentUser;
import fi.hiit.dime.data.*;
import fi.hiit.dime.database.*;
import java.util.Date;
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

//------------------------------------------------------------------------------

@RestController
@RequestMapping("/api/data")
public class DataController {
    private static final Logger LOG = 
	LoggerFactory.getLogger(DataController.class);

    // Mongodb repositories
    private final EventDAO eventDAO;
    private final InformationElementDAO infoElemDAO;

    @Autowired
    DataController(EventDAO eventDAO,
		   InformationElementDAO infoElemDAO) {
	this.eventDAO = eventDAO;
	this.infoElemDAO = infoElemDAO;
    }

    //--------------------------------------------------------------------------

    protected void eventLog(String eventName, User user, Event input) {
	LOG.info("{} for user {} from {} at {}, with actor {}",
		 eventName, user.username, input.origin, new Date(), input.actor);
    }

    //--------------------------------------------------------------------------

    protected User getUser(Authentication auth) {
	CurrentUser currentUser = (CurrentUser)auth.getPrincipal();
	return currentUser.getUser();
    }

    //--------------------------------------------------------------------------

    @RequestMapping(value="/searchevent", method = RequestMethod.POST)
    public ResponseEntity<SearchEvent> searchEvent(Authentication auth, 
						   @RequestBody SearchEvent input) {
	User user = getUser(auth);
	input.user = user;

	eventDAO.save(input);

	eventLog("SearchEvent", user, input);
	return new ResponseEntity<SearchEvent>(input, HttpStatus.OK);
    }

    //--------------------------------------------------------------------------

    @RequestMapping(value="/desktopevent", method = RequestMethod.POST)
    public ResponseEntity<DesktopEvent> documentEvent(Authentication auth, 
						      @RequestBody DesktopEvent input) {
	User user = getUser(auth);
	input.user = user;

	InformationElement res = input.targettedResource;

	// FIXME this should probably be generalised into its own function
	if (res != null) {
	    if (!res.isStub()) {
		res.user = user;
		infoElemDAO.save(res);
	    } else { // expand from if only a stub res was included
		InformationElement expandedRes = infoElemDAO.findById(res.id);
		if (expandedRes != null) {
		    LOG.info("Expanded resouce for " + expandedRes.uri);
		    // don't copy the text, takes too much space
		    expandedRes.plainTextContent = null; 
		    input.targettedResource = expandedRes;
		}
	    }
	} 

	eventDAO.save(input);
	
	eventLog("DesktopEvent", user, input);
	return new ResponseEntity<DesktopEvent>(input, HttpStatus.OK);
    }
}
