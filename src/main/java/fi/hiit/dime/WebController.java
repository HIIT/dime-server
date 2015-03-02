package fi.hiit.dime;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.beans.factory.annotation.Autowired;

@Controller
public class WebController {

    private final ZeitgeistEventRepository zeitgeistEventRepository;

    @Autowired
    WebController(ZeitgeistEventRepository zeitgeistEventRepository) {
	this.zeitgeistEventRepository = zeitgeistEventRepository;
    }

    @RequestMapping("/")
    public String root(Model model) {
	model.addAttribute("name", "World");
        model.addAttribute("events", zeitgeistEventRepository.findAll());
        return "root";
    }

}
