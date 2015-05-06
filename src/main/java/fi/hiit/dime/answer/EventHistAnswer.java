package fi.hiit.dime.answer;

//------------------------------------------------------------------------------

import fi.hiit.dime.database.EventCount;
import java.util.Date;
import java.util.List;

//------------------------------------------------------------------------------

public class EventHistAnswer {
    public Date date;
    public List<EventCount> hist;

    public EventHistAnswer(Date date, List<EventCount> hist) {
	this.date = date;
	this.hist = hist;
    }
}
