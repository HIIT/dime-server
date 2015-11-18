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

import java.util.List;

import javax.persistence.CascadeType;
import javax.persistence.Column;
import javax.persistence.JoinColumn;
import javax.persistence.ElementCollection;
import javax.persistence.Entity;
import javax.persistence.OneToMany;

/**
   A detailed reading event.
   Also see https://github.com/HIIT/PeyeDF/wiki/Data-Format/.
*/
@Entity
public class ReadingEvent extends DesktopEvent {
    /** Boolean indicating if the event is a summary sent at the end of reading.
    */
    public Boolean isSummary;

    /** Id identifying this reading session.
     * All ReadingEvents generated during one session (from document open to document close) should have the same sessionId.
     */
    public String sessionId;

    /** List of strings that were searched for, found and selected by user, during this summary event (for summary events).
     */
    @ElementCollection(targetClass = String.class)
    public List<String> foundStrings;

    /** Proportion of document which was read (for summary events)
     */
    public double proportionRead;

    /** Proportion of document which was marked as "interesting" (for summary events)
     */
    public double proportionInteresting;

    /** Proportion of document which was marked as "critical" (for summary events)
     */
    public double proportionCritical;

    /** A vector representing the page numbers currently being considered (number within PDF document).
     * These are the visible pages, or pages being referenced to in any other way (for events containing "interesting" paragraphs).
     * A number representing the page number in the given document, starting from 0. */
    @ElementCollection(targetClass = Integer.class)
    public List<Integer> pageNumbers;
    
    /** A vector representing the page numbers currently being considered (ORIGINAL page number).
     * These are the visible pages, or pages being referenced to in any other way (for events containing "interesting" paragraphs).
     * This means you could get page 500 even if you PDF is 2 pages long, if that was the page in the source journal, for example. */
    @ElementCollection(targetClass = String.class)
    public List<String> pageLabels;
    
    /** A list of rectangles representing where the relevant (viewport, seen, interesting, etc.) paragraphs are. 
     * All the rects should fit within the page. Rect dimensions refer to points in a 72 dpi space where the bottom left is the origin,
     * as in Apple's PDFKit. A page in US Letter format (often used for papers) translates to approx 594 x 792 points. */
    @OneToMany(cascade=CascadeType.ALL)
    @JoinColumn(name="event_id", referencedColumnName="id")
    public List<Rect> pageRects;

    /** The scale factor currently being used (1 = 100% size, 2 = 200%, etc).
     */
    public double scaleFactor;

    /** Eye tracking data for this event, one entry per page (pageEyeData contains page index, from 0).
     */
    @OneToMany(cascade=CascadeType.ALL)
    @JoinColumn(name="event_id", referencedColumnName="id")
    public List<PageEyeData> pageEyeData;

    /** Plain text content of text currently displayed on screen. */
    @Column(columnDefinition="longtext")
    public String plainTextContent;
}
