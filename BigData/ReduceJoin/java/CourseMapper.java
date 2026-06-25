package com.example.join;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class CourseMapper extends Mapper<LongWritable, Text, Text, Text> {

    private static final String COURSE_TAG = "course~";
    private static final String DATA_SEPARATOR = ",";

    @Override
    public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString();

        // Skip header row
        if (line.startsWith("Course_ID")) {
            return;
        }

        String[] parts = line.split(DATA_SEPARATOR);

        // Expected format: Course_ID, Course_Name, Instructor, ...
        // We need at least 3 parts for Course_ID, Course_Name, Instructor
        if (parts.length >= 3) {
            String courseId = parts[0].trim();
            String courseName = parts[1].trim();
            String instructor = parts[2].trim();

            // Emit (Course_ID, 'course~'+ Course_Name +','+ Instructor)
            context.write(new Text(courseId), new Text(COURSE_TAG + courseName + DATA_SEPARATOR + instructor));
        } else {
            // Handle malformed lines or log errors if necessary
            context.getCounter("CourseMapper", "Malformed Records").increment(1);
        }
    }
}
