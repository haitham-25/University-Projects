package com.example.join;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class EnrollmentJoinReducer extends Reducer<Text, Text, Text, Text> {

    private static final String COURSE_TAG = "course~";
    private static final String ENROLL_TAG = "enroll~";
    private static final String DATA_SEPARATOR = ",";
    private static final String UNKNOWN_COURSE_NAME = "Unknown Course";
    private static final String UNKNOWN_INSTRUCTOR = "Unknown Instructor";

    @Override
    protected void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
        String courseName = null;
        String instructor = null;
        List<String> studentNames = new ArrayList<>();

        for (Text value : values) {
            String valStr = value.toString();
            if (valStr.startsWith(COURSE_TAG)) {
                String courseInfo = valStr.substring(COURSE_TAG.length()); // Course_Name,Instructor
                String[] courseParts = courseInfo.split(DATA_SEPARATOR, 2);
                if (courseParts.length >= 1) {
                    courseName = courseParts[0].trim();
                }
                if (courseParts.length >= 2) {
                    instructor = courseParts[1].trim();
                }
            } else if (valStr.startsWith(ENROLL_TAG)) {
                String enrollmentDetail = valStr.substring(ENROLL_TAG.length()); // Student_Name,EnrollmentDate
                String[] enrollParts = enrollmentDetail.split(DATA_SEPARATOR, 2);
                if (enrollParts.length >= 1) {
                    studentNames.add(enrollParts[0].trim());
                }
            }
        }

        // Handle missing course information
        String finalCourseName = (courseName != null) ? courseName : UNKNOWN_COURSE_NAME;
        String finalInstructor = (instructor != null) ? instructor : UNKNOWN_INSTRUCTOR;

        for (String studentName : studentNames) {
            // Output: Course_Name, Instructor, Student_Name
            // The output key will be Course_Name, and value will be Instructor,Student_Name
            // With mapreduce.output.textoutputformat.separator set to ',', the final output will be: Course_Name,Instructor,Student_Name
            context.write(new Text(finalCourseName), new Text(finalInstructor + DATA_SEPARATOR + studentName));
        }
    }
}
