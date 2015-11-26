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

package fi.hiit.dime.data;

import com.fasterxml.jackson.annotation.*;
import org.springframework.data.jpa.domain.AbstractPersistable;

import java.util.Calendar;
import java.util.Date;

import javax.persistence.Embedded;
import javax.persistence.Entity;
import javax.persistence.FetchType;
import javax.persistence.Inheritance;
import javax.persistence.InheritanceType;
import javax.persistence.JoinColumn;

/**
   Abstract class for all events.
*/
@JsonInclude(value=JsonInclude.Include.NON_NULL)
@JsonTypeInfo(use=JsonTypeInfo.Id.NAME, include=JsonTypeInfo.As.PROPERTY, property="@type")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler", "new"})
@JsonSubTypes({
	    @JsonSubTypes.Type(value=fi.hiit.dime.data.FeedbackEvent.class, name="FeedbackEvent"),
	    @JsonSubTypes.Type(value=fi.hiit.dime.data.Document.class, name="Document"),
	    @JsonSubTypes.Type(value=fi.hiit.dime.data.DesktopEvent.class, name="DesktopEvent"),
	    @JsonSubTypes.Type(value=fi.hiit.dime.data.ReadingEvent.class, name="ReadingEvent"),
	    @JsonSubTypes.Type(value=fi.hiit.dime.data.MessageEvent.class, name="MessageEvent"),
	    @JsonSubTypes.Type(value=fi.hiit.dime.data.SearchEvent.class, name="SearchEvent"),
})
@Entity
@Inheritance(strategy=InheritanceType.SINGLE_TABLE)
public abstract class Event extends DiMeData {
    /** The program that produced the event, e.g. "Firefox".
     */
    public String actor;

    /** Typically the host name of the computer where the event was generated.
     */
    public String origin;

    /** Place where the event happened.
     */
    @Embedded
    public Location location;

    /** Time stamp when the event was started. Format example: 2015-08-11T12:56:53Z
     */
    public Date start;

    /** Time stamp when the event ended - DiMe can fill this if duration was supplied.
     */
    public Date end;

    /** Duration of event in seconds - DiMe can fill this if end time was supplied.
     */
    public double duration;

    /** Make sure start, end and duration times are consistent. 
     */
    @Override
    public void autoFill() {
	Calendar cal = Calendar.getInstance();
	int dur = (int)(duration*1000.0);

	if (start == null && end != null) {
	    cal.setTime(end);
	    cal.add(Calendar.MILLISECOND, -dur);
	    start = cal.getTime();
	} else if (start != null && end == null) {
	    cal.setTime(start);
	    cal.add(Calendar.MILLISECOND, dur);
	    end = cal.getTime();
	} else if (start != null && !start.equals(end)) {
	    duration = (end.getTime() - start.getTime())/1000.0;
	}
    } 
}
