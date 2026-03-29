import re

with open('services/ui-app/src/app/vendor/page.tsx', 'r') as f:
    code = f.read()

# Replace vendor UI to add "Check In" button for "Vendor Dispatched" status

patch = """
                  <div className="mt-2 mb-4 flex flex-wrap gap-2">
                      {job.approval_status === "Vendor Dispatched" && (
                          <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-bold whitespace-nowrap">
                            Awaiting Arrival
                          </span>
                      )}
                      {job.approval_status === "Vendor On Site" && (
                          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-bold whitespace-nowrap">
                            🛠️ Work in Progress
                          </span>
                      )}
                      {job.approval_status === "Ready for Payment" && (
                          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-bold whitespace-nowrap flex items-center w-max">
                            <CheckCircle className="w-3 h-3 mr-1" /> Ready for Payment
                          </span>
                      )}
                      {job.approval_status === "Rework Required" && (
                          <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-bold whitespace-nowrap flex items-center w-max">
                            <AlertCircle className="w-3 h-3 mr-1" /> Rework Required
                          </span>
                      )}
                  </div>

                  {job.approval_status === "Vendor Dispatched" && (
                      <div className="mt-4 p-4 bg-gray-100 rounded border border-gray-300 text-center">
                          <p className="text-sm text-gray-700 mb-3">Arrived at the site? Please check in to begin work.</p>
                          <button 
                            onClick={() => handeManualOverride(job.job_id, "Vendor On Site")}
                            className="flex mx-auto items-center px-4 py-2 bg-indigo-600 text-white font-bold rounded shadow hover:bg-indigo-700"
                          >
                             📱 NFC Check-In (Mock)
                          </button>
                      </div>
                  )}

                  {job.qa_notes && (
"""

code = code.replace("""
                  <div className="mt-2 mb-4">
                      {job.approval_status === "Vendor Dispatched" && (
                          <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-bold whitespace-nowrap">
                            Awaiting Fix
                          </span>
                      )}
                      {job.approval_status === "Ready for Payment" && (
                          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-bold whitespace-nowrap flex items-center w-max">
                            <CheckCircle className="w-3 h-3 mr-1" /> Ready for Payment
                          </span>
                      )}
                      {job.approval_status === "Rework Required" && (
                          <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-bold whitespace-nowrap flex items-center w-max">
                            <AlertCircle className="w-3 h-3 mr-1" /> Rework Required
                          </span>
                      )}
                  </div>

                  {job.qa_notes && (""", patch)

# Add "Vendor On Site" in filter
code = code.replace("""j.approval_status === "Vendor Dispatched" || 
        j.approval_status === "Ready for Payment" || """, """j.approval_status === "Vendor Dispatched" || 
        j.approval_status === "Vendor On Site" || 
        j.approval_status === "Ready for Payment" || """)

# Hide tools unless checked in or ready
patch2 = """
                  <hr className="my-4 border-gray-200" />
                  
                  {job.approval_status !== "Vendor Dispatched" && (
                  <div className="mt-auto">
                    <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Update Order</h4>
                    <div className="flex space-x-2 mb-2">
"""

code = code.replace("""
                  <hr className="my-4 border-gray-200" />
                  
                  <div className="mt-auto">
                    <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Update Order</h4>
                    <div className="flex space-x-2 mb-2">""", patch2)

patch3 = """
                       </button>
                    </div>
                  </div>
                  )}
                </div>

                {/* Right Side: Upload Fix Photo */}
"""

code = code.replace("""
                       </button>
                    </div>
                  </div>
                </div>

                {/* Right Side: Upload Fix Photo */}""", patch3)

patch4 = """
                {/* Right Side: Upload Fix Photo */}
                <div className="p-6 md:w-1/3 flex flex-col justify-center items-center bg-gray-50 border-l border-gray-200">
                  {job.approval_status === "Vendor Dispatched" ? (
                    <div className="text-center text-gray-400 text-sm">
                       Please Check IN first to upload repair evidence.
                    </div>
                  ) : job.post_repair_media_url ? ("""

code = code.replace("""
                {/* Right Side: Upload Fix Photo */}
                <div className="p-6 md:w-1/3 flex flex-col justify-center items-center bg-gray-50 border-l border-gray-200">
                  {job.post_repair_media_url ? (""", patch4)

patch5 = """
                          disabled={uploadingJobId === job.job_id}
                        />
                      </label>
                    </div>
                  )}
                </div>
"""

code = code.replace("""
                          disabled={uploadingJobId === job.job_id}
                        />
                      </label>
                    </div>
                  )}
                </div>""", """
                          disabled={uploadingJobId === job.job_id}
                        />
                      </label>
                    </div>
                  )}
                </div>""")

with open('services/ui-app/src/app/vendor/page.tsx', 'w') as f:
    f.write(code)

