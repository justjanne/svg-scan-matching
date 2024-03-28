use fcmlib::SegmentLine;
use serde::{Deserialize, Serialize};

use crate::PointDto;

#[derive(Serialize, Deserialize)]
pub struct SegmentLineDto {
    end: PointDto,
}

impl SegmentLineDto {
    pub fn from(segment: &SegmentLine) -> SegmentLineDto {
        SegmentLineDto {
            end: PointDto::from(&segment.end)
        }
    }

    pub fn into(&self) -> SegmentLine {
        SegmentLine {
            end: (&self.end).into()
        }
    }
}
