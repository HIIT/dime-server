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
    // Mongodb repositories
    private final EventDAO eventDAO;
    private final InformationElementDAO infoElemDAO;

    @Autowired
    DataController(EventDAO eventDAO,
		   InformationElementDAO infoElemDAO) {
	this.eventDAO = eventDAO;
	this.infoElemDAO = infoElemDAO;
    }

    @RequestMapping(value="/documentevent", method = RequestMethod.POST)
    public ResponseEntity<DocumentEvent> documentEvent(Authentication authentication, 
						       @RequestBody DocumentEvent input) {

	CurrentUser currentUser = (CurrentUser)authentication.getPrincipal();
	User user = currentUser.getUser();
	
	Date date = new Date();

	input.user = user;

	// FIXME: add needed fields here, e.g. uri:
	//
	// db.zgEvent.find( { "subject.uri": null}).forEach(
	//     function(e) { 
	// 	x=db.zgSubject.findOne({_id: e.subject._id}); 
	// 	db.zgEvent.update({ '_id': e._id }, 
	// 			  { $set: { 'subject.uri': x.uri } } );
	//     } 
	// )

	Document subject = input.subject;
	if (subject != null) {
	    if (!subject.isStub()) {
		subject.user = user;
		infoElemDAO.save(subject);
	    } else { // expand from if only a stub subject was included
		Document expandedSubject = (Document)infoElemDAO.findById(subject.id);
		if (expandedSubject != null) {
		    System.out.println("Expanded subject for " + expandedSubject.uri);
		    // don't copy the text, takes too much space
		    expandedSubject.plainTextContent = null; 
		    input.subject = expandedSubject;
		}
	    }
	} 
	eventDAO.save(input);
	
	System.out.printf("Event for user %s from %s at %s [%s]\n",
			  user.username, input.origin, date, input.actor);
	return new ResponseEntity<DocumentEvent>(input, HttpStatus.OK);
    }
}
