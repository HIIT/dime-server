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

import fi.hiit.dime.answer.*;
import fi.hiit.dime.database.*;
import java.util.Calendar;
import java.util.Date;
import java.util.ArrayList;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

//------------------------------------------------------------------------------

@RestController
@RequestMapping("/api/answer")
public class AnswerController {
    private final EventDAO eventDAO;

    @Autowired
    AnswerController(EventDAO eventDAO) {
        this.eventDAO = eventDAO;
    }

    // @RequestMapping(value="/eventhist", method = RequestMethod.GET)
    // public ResponseEntity<List<EventHistAnswer>>
    //  eventHist(@RequestParam(defaultValue="false") String perc,
    //            @RequestParam(defaultValue="actor") String groupBy) {

    //  List<EventHistAnswer> answer = new ArrayList<EventHistAnswer>();

    //  // Set calendar to tomorrow at 00:00:00
    //  Calendar cal = Calendar.getInstance();
    //  cal.add(Calendar.DAY_OF_MONTH, 1);
    //  cal.set(Calendar.HOUR, 0);
    //  cal.set(Calendar.MINUTE, 0);
    //  cal.set(Calendar.SECOND, 0);
    //  cal.set(Calendar.MILLISECOND, 0);

    //  for (int i=0; i<10; i++) {
    //      Date toDate = cal.getTime();
    //      cal.add(Calendar.DAY_OF_MONTH, -1);
    //      Date fromDate = cal.getTime();

    //      List<EventCount> results = eventDAO.eventHist(groupBy, fromDate, 
    //                                                    toDate,
    //                                                    !perc.equals("false"));

    //      answer.add(new EventHistAnswer(fromDate, results));
    //  }

    //  return new ResponseEntity<List<EventHistAnswer>>(answer, HttpStatus.OK);
    // }
}
