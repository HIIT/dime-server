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

/**
   Class representing a rectangle in a two dimensions (maps to the ReadingRect struct in PeyeDF).
*/
public class Rect {
    /** The minimum value.
     */
    public Point origin;

    /** The maximum value.
     */
    public Size size;

    /** Reading class of this rectangle (refer to the CLASS_* constants).
     */
    public int readingClass;

    /** Unspecified reading class
     */
    public static final int CLASS_UNSET = 0;

    /** Class for reading viewport rectangles (standard without eye tracking).
     */
    public static final int CLASS_VIEWPORT = 10;

    /** Class for eye tracking read text.
     */
    public static final int CLASS_READ = 20;

    /** Class for eye tracking "interesting" rectangles.
     */
    public static final int CLASS_INTERESTING = 25;

    /** Class for eye tracking "critical" rectangles.
     */
    public static final int CLASS_CRITICAL = 30;
}
