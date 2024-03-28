use fcmlib::Point;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct PointDto {
    x: i32,
    y: i32,
}

impl From<&Point> for PointDto {
    fn from(point: &Point) -> PointDto {
        PointDto {
            x: point.x,
            y: point.y,
        }
    }
}

impl Into<Point> for &PointDto {
    fn into(self) -> Point {
        Point {
            x: self.x,
            y: self.y,
        }
    }
}

impl Into<Point> for PointDto {
    fn into(self) -> Point {
        Into::into(&self)
    }
}
