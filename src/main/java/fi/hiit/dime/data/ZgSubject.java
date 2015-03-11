package fi.hiit.dime.data;

public class ZgSubject extends DiMeData {
    public String uri;
    public String mimetype;
    public String storage;
    public String text;

    public boolean isStub() {
	return uri == null || uri.isEmpty();
    }
}
