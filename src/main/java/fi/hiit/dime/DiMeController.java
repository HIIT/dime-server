package fi.hiit.dime;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.beans.factory.annotation.Autowired;

@RestController
public class DiMeController {
    private final ZeitgeistEventRepository zeitgeistEventRepository;
    private final ZeitgeistSubjectRepository zeitgeistSubjectRepository;
    

    @Autowired
    DiMeController(ZeitgeistEventRepository zeitgeistEventRepository,
		   ZeitgeistSubjectRepository zeitgeistSubjectRepository) {
	this.zeitgeistEventRepository = zeitgeistEventRepository;
	this.zeitgeistSubjectRepository = zeitgeistSubjectRepository;
    }

    @RequestMapping(value="/logger/zeitgeist", method = RequestMethod.POST)
    public ResponseEntity<ZeitgeistEvent> zeitgeistLogger(@RequestBody ZeitgeistEvent input) {
	ZeitgeistEvent event = zeitgeistEventRepository.save(input);
	zeitgeistSubjectRepository.save(input.getSubject());
	
	System.out.println("zeitgeistLogger: " + input.getActor());
	return new ResponseEntity<ZeitgeistEvent>(input, HttpStatus.OK);
    }
}
