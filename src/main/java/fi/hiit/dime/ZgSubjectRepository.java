package fi.hiit.dime;

import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;

public interface ZgSubjectRepository extends MongoRepository<ZgSubject, String> {

    //public List<ZgSubject> findByActor(String actor);
}
