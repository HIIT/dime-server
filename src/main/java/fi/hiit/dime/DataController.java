package fi.hiit.dime;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.Date;

import fi.hiit.dime.database.*;
import fi.hiit.dime.data.*;

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
    public ResponseEntity<ZgEvent> zgEvent(@RequestBody ZgEvent input) {
	Date date = new Date();

	ZgEvent event = zgEventRepository.save(input);

	ZgSubject subject = input.subject;
	if (!subject.isStub())
	    zgSubjectRepository.save(subject);
	
	System.out.println("Event from " + input.origin + " at " + date +
			   " [" + input.actor + "]");
	return new ResponseEntity<ZgEvent>(input, HttpStatus.OK);
    }
}
