package fi.hiit.dime;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.beans.factory.annotation.Autowired;

import fi.hiit.dime.database.ZgEventRepository;

@Controller
public class WebController {

    private final ZgEventRepository zgEventRepository;

    @Autowired
    WebController(ZgEventRepository zgEventRepository) {
	this.zgEventRepository = zgEventRepository;
    }

    @RequestMapping("/")
    public String root(Model model) {
        return "root";
    }

    @RequestMapping("/log")
    public String log(Model model) {
	model.addAttribute("name", "World");
        model.addAttribute("events", zgEventRepository.findAllByOrderByTimestampDesc());
        return "log";
    }

    @RequestMapping("/login")
    public String login(Model model) {
	return "login";
    }
}
