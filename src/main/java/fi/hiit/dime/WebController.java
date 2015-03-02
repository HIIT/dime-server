package fi.hiit.dime;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.beans.factory.annotation.Autowired;

@Controller
public class WebController {

    private final AppEventRepository appEventRepository;

    @Autowired
    WebController(AppEventRepository appEventRepository) {
	this.appEventRepository = appEventRepository;
    }

    @RequestMapping("/")
    public String root(Model model) {
	model.addAttribute("name", "World");
        model.addAttribute("appevents", appEventRepository.findAll());
        return "root";
    }

}
