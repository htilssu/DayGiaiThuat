"use client";

interface StatsCard {
  title: string;
  value: string;
  change: string;
  isIncrease: boolean;
  icon?: string;
}

interface TableData {
  id: string;
  name: string;
  email: string;
  status: "Active" | "Inactive" | "Pending";
  date: string;
}

interface Activity {
  text: string;
  time: string;
  type: "user" | "system" | "security" | "update";
}

export default function Overview() {
  const stats: StatsCard[] = [
    {
      title: "Total Users",
      value: "1,234",
      change: "+12.5%",
      isIncrease: true,
      icon: "👥",
    },
    {
      title: "Active Sessions",
      value: "423",
      change: "+5.25%",
      isIncrease: true,
      icon: "🔵",
    },
    {
      title: "Total Revenue",
      value: "$12,345",
      change: "-2.5%",
      isIncrease: false,
      icon: "💰",
    },
    {
      title: "Conversion Rate",
      value: "2.5%",
      change: "+0.5%",
      isIncrease: true,
      icon: "📈",
    },
  ];

  const recentActivity: Activity[] = [
    { text: "New user registration", time: "5 minutes ago", type: "user" },
    { text: "System update completed", time: "2 hours ago", type: "system" },
    { text: "Security alert detected", time: "3 hours ago", type: "security" },
    { text: "Database backup completed", time: "4 hours ago", type: "system" },
    { text: "New feature deployed", time: "5 hours ago", type: "update" },
  ];

  const tableData: TableData[] = [
    {
      id: "1",
      name: "John Doe",
      email: "john@example.com",
      status: "Active",
      date: "2024-03-20",
    },
    {
      id: "2",
      name: "Jane Smith",
      email: "jane@example.com",
      status: "Inactive",
      date: "2024-03-19",
    },
    {
      id: "3",
      name: "Bob Johnson",
      email: "bob@example.com",
      status: "Active",
      date: "2024-03-18",
    },
    {
      id: "4",
      name: "Alice Brown",
      email: "alice@example.com",
      status: "Pending",
      date: "2024-03-17",
    },
  ];

  const getActivityIcon = (type: Activity["type"]) => {
    switch (type) {
      case "user":
        return "👤";
      case "system":
        return "🔧";
      case "security":
        return "🔒";
      case "update":
        return "🚀";
      default:
        return "📝";
    }
  };

  const getStatusColor = (status: TableData["status"]) => {
    switch (status) {
      case "Active":
        return "bg-green-100 text-green-700";
      case "Inactive":
        return "bg-gray-100 text-gray-700";
      case "Pending":
        return "bg-yellow-100 text-yellow-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div>
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-200">
            <div className="flex items-center mb-4">
              <span className="text-2xl mr-2">{stat.icon}</span>
              <h3 className="text-sm text-gray-500">{stat.title}</h3>
            </div>
            <div className="flex items-center justify-between">
              <p className="text-2xl font-semibold text-gray-800">
                {stat.value}
              </p>
              <span
                className={`text-sm px-2 py-1 rounded-full ${
                  stat.isIncrease
                    ? "bg-green-100 text-green-700"
                    : "bg-red-100 text-red-700"
                }`}>
                {stat.change}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-semibold mb-6 text-gray-800">
              Recent Activity
            </h2>
            <div className="space-y-6">
              {recentActivity.map((activity, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-3 pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                  <span className="text-xl mt-1">
                    {getActivityIcon(activity.type)}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm text-gray-700">{activity.text}</p>
                    <span className="text-xs text-gray-400 mt-1">
                      {activity.time}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Data Table */}
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-800">
                Recent Users
              </h2>
              <button className="text-primary hover:text-primary-dark text-sm font-medium">
                View All
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Name
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Email
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Status
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {tableData.map((user) => (
                    <tr
                      key={user.id}
                      className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 text-sm text-gray-800">
                        {user.name}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {user.email}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-1 text-xs rounded-full ${getStatusColor(
                            user.status
                          )}`}>
                          {user.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {user.date}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
