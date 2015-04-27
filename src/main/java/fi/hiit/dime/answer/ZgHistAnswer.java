package fi.hiit.dime.answer;

//------------------------------------------------------------------------------

import fi.hiit.dime.database.ZgCount;
import java.util.Date;
import java.util.List;

//------------------------------------------------------------------------------

public class ZgHistAnswer {
    public Date date;
    public List<ZgCount> hist;

    public ZgHistAnswer(Date date, List<ZgCount> hist) {
	this.date = date;
	this.hist = hist;
    }
}
