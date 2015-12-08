package fi.hiit.dime.database;

import fi.hiit.dime.data.Event;

public class EventCount {
    public String value;
    public long count;
    public double perc;

    public EventCount(String value, long count) {
	this.value = value;
	this.count = count;
    }
}	

