/*
  Copyright (c) 2016 University of Helsinki

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

import javax.persistence.Entity;
import javax.persistence.FetchType;
import javax.persistence.JoinColumn;
import javax.persistence.ManyToOne;
import javax.persistence.Inheritance;
import javax.persistence.InheritanceType;

/**
   Class representing a relation to an Event.
*/
@Entity
@Inheritance(strategy=InheritanceType.SINGLE_TABLE)
public class EventRelation extends DiMeDataRelation<Event> {
    public EventRelation(Event event, double weight, String actor, boolean validated) {
        this.event = event;
        this.weight = weight;
        this.actor = actor;
        this.validated = validated;
    }

    public EventRelation(Event event, double weight, String actor) {
        this(event, weight, actor, false);
    }

    public EventRelation() {
        this(null, 0.0, "", false);
    }

    @Override
    public Event getData() {
        return this.event;
    }

    @Override
    public void setData(Event event) {
        this.event = event;
    }

    /** The related event. */
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "event_id")
    public Event event;
}
