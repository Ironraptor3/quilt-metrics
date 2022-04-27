package modification;

//Tools (static imports for elegance)
import static modification.Tools.*;

import java.awt.Rectangle;

import org.vizweb.quadtree.Quadtree;
import org.vizweb.quadtree.QuadtreeNode;

import com.googlecode.javacv.cpp.opencv_core.IplImage;
import static com.googlecode.javacv.cpp.opencv_core.cvAbsDiff;
import static com.googlecode.javacv.cpp.opencv_core.cvCountNonZero;
import static com.googlecode.javacv.cpp.opencv_core.cvFlip;

public class SymmetryFixes {
	
	/**
	 * Gets the diagonal symmetry between two quadrants, as defined in vizhub.
	 * This method cannot return NaN.
	 * @param q1 The first quadrant of the quadtree to compare
	 * @param q2 The second quadrant of the quadtree to compare
	 * @return The diagonal symmetry between the two quadrants
	 */
	private enum FlipType {
		HORIZONTAL, VERTICAL, DIAGONAL;
	}
	
	private static double symmetryFix(QuadtreeNode q1, QuadtreeNode q2, FlipType ft) {
		if (q1 != null && q2 != null
				&& q1.getROI().getWidth()  == q2.getROI().getWidth()
				&& q1.getROI().getHeight() == q2.getROI().getHeight() 
				&& q1.getROI().getWidth() > 0
				&& q1.getROI().getHeight() > 0) {
		IplImage i1 = moddedBinaryRepresentation(new Quadtree(q1), -1),
				i2 = moddedBinaryRepresentation(new Quadtree(q2), -1),
				temp = i2.clone();
		
		if (ft == FlipType.HORIZONTAL) {
			cvFlip(temp, i2, 1);
		}
		else if (ft == FlipType.VERTICAL) {
			cvFlip(temp, i2, 0);
		}
		else {
			cvFlip(i2, temp, 0); // Flip into temp first
			//i2 = temp.clone();
			cvFlip(temp, i2, 1); //Then flip again
		}
		
		IplImage mask = IplImage.createCompatible(i1);
		cvAbsDiff(i1, i2, mask);
		return 1D - 1D*cvCountNonZero(mask) / (i1.width()*i1.height());
		}
		else {
			return 1D;
		}
	}
	
	/**
	 * Calculates the horizontal symmetry of a Quadtree
	 * 
	 * This approach averages the two quadrants, covering both halves.
	 * @param qt The quadtree to calculate the horizontal symmetry of
	 * @return The horizontal symmetry of the quadtree
	 */
	public static double computeHorizontalSymmetryFix(Quadtree qt) {
		QuadtreeNode[] children = getChildrenRefl(qt.getRoot());
		double w1 = symmetryFix(children[0], children[3], FlipType.HORIZONTAL);
		double w2 = symmetryFix(children[1], children[2], FlipType.HORIZONTAL);
		return (w1+w2)/2;
	}
	
	/**
	 * Calculates the vertical symmetry of a Quadtree
	 * 
	 * This approach averages the two quadrants, covering both halves.
	 * @param qt The quadtree to calculate the vertical symmetry of
	 * @return The vertical symmetry of the quadtree
	 */
	public static double computeVerticalSymmetryFix(Quadtree qt) {
		QuadtreeNode[] children = getChildrenRefl(qt.getRoot());
		double w1 = symmetryFix(children[0], children[1], FlipType.VERTICAL);
		double w2 = symmetryFix(children[2], children[3], FlipType.VERTICAL);
		return (w1+w2)/2;
	}
	
	/**
	 * Calculates the diagonal symmetry of a Quadtree
	 * 
	 * This approach averages the two quadrants, covering both diagonals.
	 * @param qt The quadtree to calculate the diagonal symmetry of
	 * @return The diagonal symmetry of the quadtree
	 */
	public static double computeDiagonalSymmetryFix(Quadtree qt) {
		QuadtreeNode[] children = getChildrenRefl(qt.getRoot());
		double w1 = symmetryFix(children[0], children[2], FlipType.DIAGONAL);
		double w2 = symmetryFix(children[1], children[3], FlipType.DIAGONAL);
		return (w1+w2)/2;
	}
	
	/**
	 * Helper class meant to store the symmetry-based data of a Quadtree
	 * @author DanielRibaudo
	 *
	 */
	private static class SymmetryData {
		//X, Y, H, B, T, R - all defined in the corresponding research paper
		double[] data = new double[6];
		
		/**
		 * Constructor for the SymmetryData class.
		 * Calculates the data required to make symmetry comparisons.
		 * @param qt The quadtree node to get the data of
		 */
		public SymmetryData(QuadtreeNode qt) {
			if (qt != null) {
				//Calculate all
				double cx = qt.getROI().getCenterX(),
					cy = qt.getROI().getCenterY();
				for (QuadtreeNode leaf : getLeaves(qt)) {
					Rectangle roi = leaf.getROI();
					double dx = Math.abs(roi.getCenterX()-cx);
					double dy = Math.abs(roi.getCenterY()-cy);
					double t = dy/dx;
					data[0] += dx; //X
					data[1] += dy; //Y
					data[2] += roi.getHeight(); //H
					data[3] += roi.getWidth(); //B
					data[4] += Double.isFinite(t)?t:0D; //T
					data[5] += Math.sqrt(dx*dx+dy*dy); //R
				}
				
				//Normalize
				double sum = 0;
				for (double d : data) {
					sum += d;
				}
				if (sum > 0) {
					for (int i = 0; i < data.length; ++i) {
						data[i] /= sum;
					}
				}
			}
		}
		
		/**
		 * Get the average difference between this SymmetryData and another
		 * @param other The SymmetryData being compared to
		 * @return The average difference between the two data vectors
		 */
		public double compareTo(SymmetryData other) {
			double sum = 0;
			for (int i = 0; i < data.length; ++i) {
				sum += Math.abs(data[i]-other.data[i]);
			}
			return sum / data.length;
		}
	}
	
	/**
	 * Gets all of the SymmetryData for the children of the provided quadtree
	 * @param qt The quadtree to get the child-data for
	 * @return An array of SymmetryData, one for each child of the quadtree
	 */
	private static SymmetryData[] getQuadrantData(Quadtree qt) {
		QuadtreeNode[] children = getChildrenRefl(qt.getRoot());
		SymmetryData[] sd = new SymmetryData[children.length];
		for (int i = 0; i < children.length; ++i) {
			sd[i] = new SymmetryData(children[i]);
		}
		return sd;
	}
	/**
	 * Computes horizontal symmetry using the equations found in the paper
	 * @param qt The quadtree to calculate the horizontal symmetry of
	 * @return The horizontal symmetry of the given quadtree
	 */
	public static double computeHorizontalSymmetryEqn(Quadtree qt) {
		SymmetryData[] sd = getQuadrantData(qt);
		return (sd[0].compareTo(sd[3])+sd[1].compareTo(sd[2])) / 2;
	}
	/**
	 * Computes vertical symmetry using the equations found in the paper
	 * @param qt The quadtree to calculate the vertical symmetry of
	 * @return The vertical symmetry of the given quadtree
	 */
	public static double computeVerticalSymmetryEqn(Quadtree qt) {
		SymmetryData[] sd = getQuadrantData(qt);
		return (sd[0].compareTo(sd[1])+sd[2].compareTo(sd[3])) / 2;
	}
	/**
	 * Computes diagonal symmetry using the equations found in the paper
	 * @param qt The quadtree to calculate the diagonal symmetry of
	 * @return The diagonal symmetry of the given quadtree
	 */
	public static double computeDiagonalSymmetryEqn(Quadtree qt) {
		SymmetryData[] sd = getQuadrantData(qt);
		return (sd[0].compareTo(sd[2])+sd[1].compareTo(sd[3])) / 2;
	}
	
	/**
	  * Computes the average symmetry using the default Vizweb implementation. Considers horizontal, vertical, and diagonal (radial) symmetries.
	  * @param qt The quadtree to obtain the average symmetry of
	  * @return The average symmetry
	  */
	public static double computeAverageSymmetry(Quadtree qt) {
		return 1D*(computeHorizontalSymmetryFix(qt) + computeVerticalSymmetryFix(qt) + computeDiagonalSymmetryFix(qt)) / 3;
	}
	
	/**
	  * Computes the average symmetry using the equation method. Considers horizontal, vertical, and diagonal (radial) symmetries.
	  * @param qt The quadtree to obtain the average symmetry of
	  * @return The average symmetry
	  */
	public static double computeAverageSymmetryEqn(Quadtree qt) {
		return 1D*(computeHorizontalSymmetryEqn(qt)+computeVerticalSymmetryEqn(qt)+computeDiagonalSymmetryEqn(qt)) / 3;
	}
}
