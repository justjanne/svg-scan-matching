use fcmlib::PieceRestrictions;
use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize)]
pub struct PieceFlagsDto {
    licensed: bool,
    seam_allowance_enabled: bool,
    seam_allowance_locked: bool,
    aspect_ratio_locked: bool,
    test_pattern: bool,
    path_locked: bool,
    tool_locked: bool,
}

impl From<&PieceRestrictions> for PieceFlagsDto {
    fn from(restrictions: &PieceRestrictions) -> PieceFlagsDto {
        PieceFlagsDto {
            licensed: restrictions.contains(PieceRestrictions::LICENSE_DESIGN),
            seam_allowance_enabled: restrictions.contains(PieceRestrictions::SEAM_ALLOWANCE),
            seam_allowance_locked: restrictions.contains(PieceRestrictions::PROHIBITION_OF_SEAM_ALLOWANCE_SETTING),
            aspect_ratio_locked: restrictions.contains(PieceRestrictions::NO_ASPECT_RATIO_CHANGE_PROHIBITED),
            test_pattern: restrictions.contains(PieceRestrictions::TEST_PATTERN),
            path_locked: restrictions.contains(PieceRestrictions::PROHIBITION_OF_EDIT),
            tool_locked: restrictions.contains(PieceRestrictions::PROHIBITION_OF_TOOL),
        }
    }
}

impl Into<PieceRestrictions> for &PieceFlagsDto {
    fn into(self) -> PieceRestrictions {
        PieceRestrictions::from_iter(PieceRestrictions::all().iter().filter(|value| match value {
            &PieceRestrictions::LICENSE_DESIGN => self.licensed,
            &PieceRestrictions::SEAM_ALLOWANCE => self.seam_allowance_enabled,
            &PieceRestrictions::PROHIBITION_OF_SEAM_ALLOWANCE_SETTING => self.seam_allowance_locked,
            &PieceRestrictions::NO_ASPECT_RATIO_CHANGE_PROHIBITED => self.aspect_ratio_locked,
            &PieceRestrictions::TEST_PATTERN => self.test_pattern,
            &PieceRestrictions::PROHIBITION_OF_EDIT => self.path_locked,
            &PieceRestrictions::PROHIBITION_OF_TOOL => self.tool_locked,
            _ => false,
        }))
    }
}

impl Into<PieceRestrictions> for PieceFlagsDto {
    fn into(self) -> PieceRestrictions {
        Into::into(&self)
    }
}
