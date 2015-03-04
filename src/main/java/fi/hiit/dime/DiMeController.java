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
    private final ZgEventRepository zgEventRepository;
    private final ZgSubjectRepository zgSubjectRepository;
    

    @Autowired
    DiMeController(ZgEventRepository zgEventRepository,
		   ZgSubjectRepository zgSubjectRepository) {
	this.zgEventRepository = zgEventRepository;
	this.zgSubjectRepository = zgSubjectRepository;
    }

    @RequestMapping(value="/logger/zeitgeist", method = RequestMethod.POST)
    public ResponseEntity<ZgEvent> zgLogger(@RequestBody ZgEvent input) {
	ZgEvent event = zgEventRepository.save(input);
	zgSubjectRepository.save(input.getSubject());
	
	System.out.println("Event posted from: " + input.getOrigin() + " [" + input.getActor() + "]");
	return new ResponseEntity<ZgEvent>(input, HttpStatus.OK);
    }
}
