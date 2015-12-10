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

import org.springframework.data.jpa.domain.AbstractPersistable;

import javax.persistence.ElementCollection;
import javax.persistence.Entity;

import java.util.List;

/**
   Class representing points read on a specific page (in page space coordinates).
*/
@Entity
public class PageEyeData extends AbstractPersistable<Long> {
    /** Horizontal (x) coordinates
     */
    @ElementCollection(targetClass = Double.class)
    public List<Double> Xs;

    /** Vertical (y) coordinatess.
     */
    @ElementCollection(targetClass = Double.class)
    public List<Double> Ys;

    /** Pupil size.
     */
    @ElementCollection(targetClass = Double.class)
    public List<Double> Ps;

    /** Times of fixation start in microseconds.
     */
    @ElementCollection(targetClass = Long.class)
    public List<Long> startTimes;

    /** Times of fixation end in microseconds.
     */
    @ElementCollection(targetClass = Long.class)
    public List<Long> endTimes;

    /** Fixation durations in microseconds.
     */
    @ElementCollection(targetClass = Long.class)
    public List<Long> durations;

    /** Page index for this block of data.
     */
    public int pageIndex;

    /** The scale factor (zoom level) used when these data were collected (1 = 100% size, 2 = 200%, etc).
     */
    public Double scaleFactor;

    /** Unix time (note: milliseconds) indicating when this chunk of data was created (when the first chunk of fixations was received).
     */
    public Long unixt;

}
