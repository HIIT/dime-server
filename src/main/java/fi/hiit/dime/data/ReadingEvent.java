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

/**
   A detailed reading event.
   Also see https://github.com/HIIT/PeyeDF/wiki/Data-Format/.
*/
public class ReadingEvent extends DesktopEvent {
    /** Boolean indicating if the event refers to multiple pages.
    */
    public Boolean multiPage;

    /** A vector representing the page numbers currently being displayed (number within PDF document).
     * A number representing the page number in the given document, starting from 0.
     * These should be in the same order as visiblePageLabels and pageRects. */
    public int[] visiblePageNumbers;
    
    /** A vector representing the page numbers currently being displayed (ORIGINAL page number).
     * This means you could get page 500 even if you PDF is 2 pages long, if that was the page in the source journal, for example.
     * These should be in the same order as visiblePageNumbers and pageRects. */
    public String[] visiblePageLabels;
    
    /** A list of rectangles representing where the viewport is placed for each page. 
     * All the rects should fit within the page. Rect dimensions refer to points in a 72 dpi space where the bottom left is the origin,
     * as in Apple's PDFKit. A page in US Letter format (often used for papers) translates to approx 594 x 792 points.
     * These should be in the same order as visiblePageNumbers and visiblePageLabels. */
    public List<Rect> pageRects;

    /** The proportion of the document currently being displayed on screen.
     For example, 0.25, 0.50 means that we are seeing from the first quarter until half the document (if a document has 4 pages then it means we are
     seeing page 2) although numbers wouldn't generally be so nicely rounded. 
     */
    public Range proportion;

    /** Plain text content of text currently displayed on screen. */
    public String plainTextContent;
}
