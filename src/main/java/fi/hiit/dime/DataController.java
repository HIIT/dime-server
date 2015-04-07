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
    private final ZgEventRepository zgEventRepository;
    private final ZgSubjectRepository zgSubjectRepository;

    @Autowired
    DataController(ZgEventRepository zgEventRepository,
		   ZgSubjectRepository zgSubjectRepository) {
	this.zgEventRepository = zgEventRepository;
	this.zgSubjectRepository = zgSubjectRepository;
    }

    @RequestMapping(value="/zgevent", method = RequestMethod.POST)
    public ResponseEntity<ZgEvent> zgEvent(Authentication authentication, 
					   @RequestBody ZgEvent input) {

	CurrentUser currentUser = (CurrentUser)authentication.getPrincipal();
	User user = currentUser.getUser();
	
	Date date = new Date();

	input.user = user;
	ZgEvent event = zgEventRepository.save(input);

	ZgSubject subject = input.subject;
	if (subject != null) {
	    subject.user = user;
	    if (!subject.isStub()) {
		zgSubjectRepository.save(subject);
	    }
	}
	
	System.out.println("Event from " + input.origin + " at " + date +
			   " [" + input.actor + "]");
	return new ResponseEntity<ZgEvent>(input, HttpStatus.OK);
    }
}
