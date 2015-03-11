package fi.hiit.dime;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.List;

import fi.hiit.dime.database.*;
import fi.hiit.dime.answer.*;

@RestController
@RequestMapping("/api/answer")
public class AnswerController {
    // Mongodb repositories
    private final ZgEventRepository zgEventRepository;
    private final ZgSubjectRepository zgSubjectRepository;

    @Autowired
    AnswerController(ZgEventRepository zgEventRepository,
		   ZgSubjectRepository zgSubjectRepository) {
	this.zgEventRepository = zgEventRepository;
	this.zgSubjectRepository = zgSubjectRepository;
    }

    @RequestMapping(value="/zghist", method = RequestMethod.GET)
    public ResponseEntity<List<ZgCount>> zgHist(@RequestParam(defaultValue="false") String perc) {
	List<ZgCount> results = zgEventRepository.zgHist(!perc.equals("false"));
	return new ResponseEntity<List<ZgCount>>(results, HttpStatus.OK);
    }
}
