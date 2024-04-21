using Godot;
using System;
using System.Collections.Generic;

using Vector2 = Godot.Vector2;
using EQ = System.Collections.Generic.PriorityQueue<BenOtt.Event, float>;
using System.ComponentModel.Design;

/// <summary>
/// An implementation of Bentley–Ottmann algorithm for line segment intersection detection.
/// </summary>
/// Based on https://www.cs.cmu.edu/~15451-f17/lectures/lec21-sweepline.pdf
public partial class BenOtt : Godot.Node
{
	public class Segment
	{
		public Vector2 start;
		public Vector2 end;
		public Node node;

		public float Slope => (end.Y - start.Y) / (end.X - start.X);
		public float YIntercept => start.Y - Slope * start.X;
		public float ValueAt(float x) => Slope * x + YIntercept;
	}

	public class Event
	{
		public enum Type
		{
			Start,
			End,
			Intersection
		}

		public Type type;

		public float x;

		public Segment segment1;
		// Only for intersection events
		public Segment segment2;
	}

	bool CheckForIntersection(EQ events, float curr, Segment a, Segment b)
	{
		if (a == null || b == null)
		{
			return false;
		}

		// Find the intersection point
		if (b.Slope == a.Slope)
		{
			// Parallel lines
			GD.Print("Parallel lines");
			return false;
		}
		float x = (a.YIntercept - b.YIntercept) / (b.Slope - a.Slope);

		// If the intersection point is not within the range of the segments, return false
		float aLeft = Mathf.Min(a.start.X, a.end.X);
		float aRight = Mathf.Max(a.start.X, a.end.X);
		float bLeft = Mathf.Min(b.start.X, b.end.X);
		float bRight = Mathf.Max(b.start.X, b.end.X);
		if (x < aLeft || x > aRight || x < bLeft || x > bRight)
		{
			return false;
		}

		// Don't add previous events to the queue
		if (x <= curr)
		{
			return true;
		}

		// Don't add the same intersection twice
		foreach (var (e, _) in events.UnorderedItems) {
			if (e.x == x && e.type == Event.Type.Intersection) {
				if ((e.segment1 == a && e.segment2 == b) || (e.segment1 == b && e.segment2 == a)) {
					return true;
				}
			}
		}

		// insert the intersection event into the event queue
		Event intersectionEvent = new Event
		{
			type = Event.Type.Intersection,
			x = x,
			segment1 = a,
			segment2 = b,
		};

		events.Enqueue(intersectionEvent, x);

		return true;
	}

	private static List<Segment> GetSegments(Godot.Collections.Array<Node> nodes) {
		List<Segment> segments = new();

		foreach (var node in nodes)
		{
			Vector2 start = (Vector2)node.Get("start");
			Vector2 end = (Vector2)node.Get("end");

			if (start.X == end.X)
			{
				GD.Print("Skipping vertical line");
				continue;
			}

			// make sure that the start point is to the left of the end point
			// This makes everything easier later
			bool swapped = start.X > end.X;
			Segment segment = new Segment
			{
				start = swapped ? end : start,
				end = swapped ? start : end,
				node = node,
			};

			segments.Add(segment);
		}

		return segments;
	}

	// Stores all the events that happen
	public EQ allEvents = new();

	// Returns the positions of all the events that have happened, to be shown on screen
	public Godot.Collections.Array<float> GetEvents() {
		Godot.Collections.Array<float> results = new();
		while (allEvents.Count > 0) {
			var e = allEvents.Dequeue();
			results.Add(e.x);
		}
		return results;
	}

	// Stores the history of segments as the line sweeps
	public List<(float, Godot.Collections.Array<Node>)> segmentsOverTime = new();

	// Returns the segments for a given x position
	public Godot.Collections.Array<Node> GetSegmentsAtTime(float t) {
		Godot.Collections.Array<Node> results = new();
		foreach (var (time, segments) in segmentsOverTime) {
			if (time > t) {
				break;
			}
			results = segments;
		}
		return results;
	}

	public Godot.Collections.Array<Vector2> FindSegmentIntersections(Godot.Collections.Array<Node> nodes)
	{
        List<Segment> segments = GetSegments(nodes);

		EQ events = new();
		allEvents.Clear();
		segmentsOverTime.Clear();

		Godot.Collections.Array<Vector2> results = new();

		// for each segment S, insert its start and end events into EQ
		foreach (Segment segment in segments)
		{
			Event startEvent = new Event
			{
				type = Event.Type.Start,
				x = segment.start.X,
				segment1 = segment,
				segment2 = segment,
			};
			events.Enqueue(startEvent, startEvent.x);

			Event endEvent = new Event
			{
				type = Event.Type.End,
				x = segment.end.X,
				segment1 = segment,
				segment2 = segment,
			};
			events.Enqueue(endEvent, endEvent.x);
		}

		// create an empty balanced tree SL
		List<Segment> SL = new();

		void insert(float x, Segment s)
		{
			// Find the correct position to insert the segment
			int i = 0;
			for (; i < SL.Count; i++)
			{
				if (SL[i].ValueAt(x) > s.ValueAt(x))
				{
					break;
				}
			}
			SL.Insert(i, s);
		}

		Segment prev(Segment s)
		{
			int i = SL.IndexOf(s);
			if (i <= 0)
			{
				return null;
			}
			return SL[i - 1];
		}

		Segment next(Segment s)
		{
			int i = SL.IndexOf(s);
			if (i >= SL.Count - 1)
			{
				return null;
			}
			return SL[i + 1];
		}

		// This should never be hit
		int timeoutCounter = 0;

		// while (EQ is not empty)
		while (events.Count > 0)
		{
			timeoutCounter++;
			if (timeoutCounter > 10000)
			{
				// TODO: This should never be hit
				GD.Print("Too many events, breaking");
				return null;
			}

			var e = events.Dequeue();
			allEvents.Enqueue(e, e.x);

			var s = e.segment1;
			if (e.type == Event.Type.Start)
			{
				insert(e.x, e.segment1);
				CheckForIntersection(events, e.x, s, next(s));
				CheckForIntersection(events, e.x, s, prev(s));
			}
			else if (e.type == Event.Type.End)
			{
				CheckForIntersection(events, e.x, prev(s), next(s));
				SL.Remove(e.segment1);
			}
			else if (e.type == Event.Type.Intersection)
			{
				results.Add(new Vector2(e.x, s.ValueAt(e.x)));

				// Swap the segments
				int i = SL.IndexOf(e.segment1);
				int j = SL.IndexOf(e.segment2);
				if (i == -1 || j == -1)
				{
					GD.Print("Segment not found in SL");
					continue;
				}
				SL[i] = e.segment2;
				SL[j] = e.segment1;

				if (i > j)
				{
					// 2 is after 1
					CheckForIntersection(events, e.x, e.segment1, prev(e.segment1)); // check before 1
					CheckForIntersection(events, e.x, e.segment2, next(e.segment2)); // check after 2
				}
				else
				{
					// 1 is after 2
					CheckForIntersection(events, e.x, e.segment1, next(e.segment1)); // check after 1
					CheckForIntersection(events, e.x, e.segment2, prev(e.segment2)); // check before 2
				}
			}
		
			segmentsOverTime.Add((e.x, new Godot.Collections.Array<Node>(SL.ConvertAll(x => x.node))));
		}

		return results;
	}
}
