/*
  Copyright (c) 2015-2017 University of Helsinki

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

import java.util.Date;
import java.util.List;

import javax.persistence.Entity;
import javax.persistence.Column;
import javax.persistence.JoinColumn;
import javax.persistence.JoinTable;
import javax.persistence.ManyToMany;
import javax.persistence.CascadeType;

/**
   An event generated from the user's calendar.
*/
@Entity
public class CalendarEvent extends Event {
    /**
       The name (or title) of the event.
    */
    public String name;

    /**
       The name of the calendar where this event appeared (e.g. work, personal, etc).
    */
    public String calendar;

    /**
     * Notes associated with the event.
     */
    @Column(columnDefinition="longtext")
    public String notes;

    /**
     * In case detailed location is not available, this field stores the location as a string.
     */
    public String locString;

    /**
     * Participants (or invitees) who took part.
     */
    @ManyToMany(cascade=CascadeType.ALL)
    @JoinTable(name="calendarevent_participants", 
               joinColumns={@JoinColumn(name="calendarevent_id", referencedColumnName="id")},
               inverseJoinColumns={@JoinColumn(name="person_id", referencedColumnName="id")})
    public List<Person> participants;
}
