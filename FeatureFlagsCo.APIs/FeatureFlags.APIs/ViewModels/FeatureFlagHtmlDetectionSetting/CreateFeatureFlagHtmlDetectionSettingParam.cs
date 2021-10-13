﻿using FeatureFlags.APIs.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace FeatureFlags.APIs.ViewModels.FeatureFlagHtmlDetectionSetting
{
    public class CreateFeatureFlagHtmlDetectionSettingParam
    {
        public int EnvironmentId { get; set; }
        public bool IsActive { get; set; }
        public string FeatureFlagId { get; set; }
        public string FeatureFlagKey { get; set; }
        public string EnvironmentKey { get; set; }
        public List<CssSelectorItem> Items { get; set; }
    }
}